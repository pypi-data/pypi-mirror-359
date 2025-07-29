# eops/data/downloader.py
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List
import time

from eops.utils.logger import log
from eops.data.clients import get_data_client

def _convert_timeframe_to_ms(timeframe: str) -> int:
    """Converts timeframe string to milliseconds."""
    try:
        # 扩展支持 'w' for week
        multipliers = {'m': 60, 'h': 3600, 'd': 86400, 'w': 604800}
        unit = timeframe[-1].lower()
        if unit not in multipliers:
            raise ValueError("Unsupported timeframe unit")
        value = int(timeframe[:-1])
        return value * multipliers[unit] * 1000
    except Exception:
        raise ValueError(f"Invalid timeframe format: '{timeframe}'. Use '1m', '5m', '1h', '4h', '1d', etc.")

def _fetch_data_for_interval(
    client, 
    symbol: str, 
    timeframe: str, 
    start_ts: int, 
    end_ts: int,
    limit: int
) -> List[list]:
    """
    Fetches all data within a given time interval using an iterative approach.
    This function is robust and suitable for both full downloads and gap filling.
    """
    all_ohlcv = []
    timeframe_ms = _convert_timeframe_to_ms(timeframe)
    step_ms = limit * timeframe_ms
    
    current_ts = start_ts
    while current_ts < end_ts:
        try:
            # We use `since` to set the start and `limit` to control the approximate end.
            # `since=current_ts - 1` is a trick for APIs where 'since' or 'after' is exclusive.
            ohlcv_chunk = client.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                since=current_ts - 1,
                limit=limit
            )
            
            if ohlcv_chunk:
                all_ohlcv.extend(ohlcv_chunk)

        except Exception as e:
            log.error(f"An error occurred during a fetch request: {e}")

        # Advance timestamp by the fixed window size, not by the last timestamp in the chunk.
        # This makes the process deterministic.
        current_ts += step_ms
        time.sleep(0.25) # Be respectful to the API, especially during intensive fixing.
    
    return all_ohlcv

def download_ohlcv_data(
    exchange_id: str,
    symbol: str,
    timeframe: str,
    since: str,
    output_path: Path,
    until: Optional[str] = None,
):
    """Downloads historical OHLCV data for a specified date range."""
    log.info(f"Attempting to download data for {symbol} on {exchange_id}...")

    try:
        client = get_data_client(exchange_id)
    except (ValueError, KeyError) as e:
        log.error(e)
        return

    since_ts = int(datetime.strptime(since, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp() * 1000)
    until_ts = int(datetime.now(timezone.utc).timestamp() * 1000)
    if until:
        until_ts = int(datetime.strptime(until, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp() * 1000)

    limit = 300 if exchange_id.lower() == 'okx' else 1000
    
    log.info(f"Starting full download from {since} to {until or 'now'}")
    all_ohlcv = _fetch_data_for_interval(client, symbol, timeframe, since_ts, until_ts, limit)

    if not all_ohlcv:
        log.error("Failed to download any data. Please check your parameters.")
        return
        
    log.info(f"Downloaded {len(all_ohlcv)} total data points. Cleaning and saving...")

    df = pd.DataFrame(all_ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = pd.to_datetime(df['time'], unit='ms', utc=True)
    
    # Final, rigorous cleaning
    df = df.sort_values(by='time').drop_duplicates(subset='time', keep='first')
    df = df[(df['time'] >= pd.to_datetime(since_ts, unit='ms', utc=True)) & 
              (df['time'] < pd.to_datetime(until_ts, unit='ms', utc=True))]
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    log.info(f"💾 Successfully saved {len(df)} unique data points to: {output_path}")

def fix_ohlcv_data(file_path: Path):
    """
    Finds and fills gaps in an existing OHLCV data file.
    """
    if not file_path.exists():
        log.error(f"File not found: {file_path}")
        return

    # --- Robust Filename Parsing ---
    filename = file_path.stem
    parts = filename.split('_')
    
    if len(parts) < 3:
        log.error(f"Filename '{filename}' does not match 'exchange_symbol_timeframe' format. It needs at least 3 parts separated by '_'.")
        return
        
    exchange_id = parts[0]
    timeframe = parts[-1]
    # Re-join the middle parts to form the symbol, handling symbols with '_' or '-'
    symbol = "_".join(parts[1:-1])
    
    log.info(f"Starting data fix for {file_path}")
    log.info(f"  - Exchange: {exchange_id}, Symbol: {symbol}, Timeframe: {timeframe}")

    # Load existing data
    try:
        df = pd.read_csv(file_path, parse_dates=['time'])
        df = df.drop_duplicates(subset=['time']).set_index('time').sort_index()
        log.info(f"Loaded {len(df)} existing data points from "
                  f"{df.index.min().date()} to {df.index.max().date()}.")
    except Exception as e:
        log.error(f"Failed to load or parse CSV file: {e}")
        return

    if df.empty:
        log.warning("File is empty. Cannot perform a fix.")
        return

    # Create a complete time index
    try:
        timeframe_freq = timeframe.replace('h', 'H').replace('d', 'D').replace('m', 'T')
        start_date = df.index.min()
        end_date = df.index.max()
        full_index = pd.date_range(start=start_date, end=end_date, freq=timeframe_freq, tz='UTC')
    except ValueError as e:
        log.error(f"Could not determine frequency from timeframe '{timeframe}'. Error: {e}")
        return
    
    # Find missing timestamps
    missing_timestamps = full_index.difference(df.index)
    
    if missing_timestamps.empty:
        log.info("✅ No gaps found in the data.")
        return
        
    log.warning(f"Found {len(missing_timestamps)} missing timestamps.")

    # Group consecutive missing timestamps into fetchable intervals
    gaps = []
    if not missing_timestamps.empty:
        missing_series = missing_timestamps.to_series()
        expected_freq = pd.to_timedelta(timeframe.replace('h', 'H'))
        breaks = missing_series.diff() != expected_freq
        groups = breaks.cumsum()
        for _, group in missing_series.groupby(groups):
            gaps.append((group.min(), group.max()))

    log.info(f"Identified {len(gaps)} gaps to fill.")

    # Fetch data for each gap
    try:
        client = get_data_client(exchange_id)
        limit = 300 if exchange_id.lower() == 'okx' else 1000
    except ValueError as e:
        log.error(e)
        return
        
    new_data = []
    for i, (start_gap, end_gap) in enumerate(gaps, 1):
        log.info(f"--- Fixing gap {i}/{len(gaps)}: "
                 f"from {start_gap.strftime('%Y-%m-%d %H:%M:%S')} "
                 f"to {end_gap.strftime('%Y-%m-%d %H:%M:%S')} ---")
        
        start_ts = int(start_gap.timestamp() * 1000)
        end_ts = int(end_gap.timestamp() * 1000) + _convert_timeframe_to_ms(timeframe)
        
        chunk = _fetch_data_for_interval(client, symbol, timeframe, start_ts, end_ts, limit)
        if chunk:
            log.info(f"Fetched {len(chunk)} new data points for this gap.")
            new_data.extend(chunk)

    if not new_data:
        log.warning("Could not fetch any new data to fill gaps.")
        return

    # Merge, clean, and save
    new_df = pd.DataFrame(new_data, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    if not new_df.empty:
        new_df['time'] = pd.to_datetime(new_df['time'], unit='ms', utc=True)
    
    combined_df = pd.concat([df.reset_index(), new_df])
    final_df = combined_df.sort_values(by='time').drop_duplicates(subset='time', keep='first')
    
    final_df.to_csv(file_path, index=False)
    log.info(f"💾 Successfully fixed data. Total data points now: {len(final_df)}. Saved to {file_path}")