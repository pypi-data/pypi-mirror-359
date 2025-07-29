import io
import os
import time
import asyncio
import logging
import aioboto3
import pandas as pd
from typing import Union
from datetime import datetime
from dotenv import load_dotenv


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


load_dotenv()

class S3:
    """
    Class Responsible for paraquet files handling and management into dataframes
    """
    def __init__(self, bucket_name:str):
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        if not all([aws_access_key_id, aws_secret_access_key]):
            raise ValueError("AWS credentials not found in environment variables.")

        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.bucket = bucket_name
        self.region = 'ap-south-1'

    @staticmethod
    def preprocess_file(data_df:pd.DataFrame):
        """
        Preprocessing the data frame
        # Transformations applied
        1. Dateimte -> Datetime
        2. Setting OHLC and Marketcap to Float 
        3. Aggreation of data using mean
            - Current data is per minute 
            - Financial Ratios require per day ie 375 trading mins
        """
        try:
            data_df['datetime'] = pd.to_datetime(data_df['datetime'])

            for column in ['open', 'high', 'low', 'close', 'market_cap']:
                data_df[column] = data_df[column].astype(float)

            data_df = data_df.groupby(data_df['datetime'].dt.date).mean(numeric_only=True)
            return data_df

        except Exception as e:
            logging.error(f"ERROR S3 -> (preprocess_file): {e}")
            return None
        
        
    async def list_folder_contents(self, folder: str):
        """
        Lists all files in a given folder (prefix) in the S3 bucket.
        """
        async with aioboto3.Session().client(
            service_name="s3",
            region_name=self.region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        ) as s3:
            try:
                paginator = s3.get_paginator("list_objects_v2")
                async for result in paginator.paginate(Bucket=self.bucket, Prefix=f"{folder}/"):
                    for content in result.get("Contents", []):
                        print(f"data: {content["Key"]}")

            except Exception as e:
                logging.error(f"ERROR S3 (list_folder_content): {e}")
                return None


    async def download_parquet_to_dataframe(self, folder: str, filename: str):
        """
        Downloads paraquet file and converts to dataframe
        """
        s3_key = f"{folder}/{filename}"
    
        async with aioboto3.Session().client(
            service_name="s3",
            region_name=self.region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        ) as s3:
            try:    
                response = await s3.get_object(Bucket=self.bucket, Key=s3_key)

                async with response['Body'] as stream:
                    data = await stream.read()                                    

                buffer = io.BytesIO(data)
                df = pd.read_parquet(buffer)
                return {"status":"success", "dataframe":df, "error":None}

            except Exception as e:
                if isinstance(e,s3.exceptions.NoSuchKey):  
                    logging.error(f"ERROR S3 (download_paraquet_to_df): {e}")
                    return None  
                logging.error(f"ERROR S3 (download_paraquet_to_df): {e}")
                return None


    async def extract_trading_view_data(self, alpha_code: str, *args: Union[str, datetime]):
        """
        Extracts trading view data from S3 and filters based on datetime.

        Parameters:
        - alpha_code: The company code used as folder.
        - args: Optional datetime arguments.
            - No args: return entire DataFrame
            - 1 arg: return data for that exact date
            - 2 args: treat as (start_date, end_date) and return data in range

        Returns:
        - Filtered pandas DataFrame or None on error
        """

        # 1. Download the Parquet and preprocess
        try:
            response = await self.download_parquet_to_dataframe(folder=alpha_code, filename="minute.parquet")
            if response["status"] != "success":
                return None

            raw_df = response.get("dataframe", {})
            data_df = S3.preprocess_file(data_df=raw_df)
            if data_df is None:
                return None

            # 2. Set datetime index properly
            data_df = data_df.sort_index(ascending=True)

            # 3. Handle date filters
            if len(args) == 0 or args == None:
                result = data_df.reset_index().rename(columns={"index": "date"})
                return result

            elif len(args) == 1:
                date = pd.to_datetime(args[0]).date()
                if date in data_df.index:
                    row = data_df.loc[data_df.index == date]
                    return row.reset_index().rename(columns={"index": "date"})
                return pd.DataFrame()
            
            elif len(args) == 2:
                start = pd.to_datetime(args[0]).date() if args[0] is not None else None
                end = pd.to_datetime(args[1]).date() if args[1] is not None else None

                if start and end:
                    filtered = data_df.loc[(data_df.index >= start) & (data_df.index <= end)]
                elif start and end is None:
                    filtered = data_df.loc[data_df.index >= start]
                elif end and start is None:
                    filtered = data_df.loc[data_df.index <= end]
                else:
                    filtered = data_df
                return filtered.reset_index().rename(columns={"index": "date"})

    
        except Exception as e:
            logging.error(f"ERROR S3 -> (extract_trading_view_data): {e}")
            return None