from typing import Literal

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import UpdateOne, DESCENDING
import pandas as pd
from datetime import datetime, timezone, time

from db2_hj3415.mi import DB_NAME, DATE_FORMAT
from db2_hj3415.common.db_ops import get_collection
from . import Usdkrw, Sp500, Silver, Kospi, Kosdaq, Wti, Gold, Gbond3y, Chf, Aud, Usdidx

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'WARNING')

T = Sp500 | Kospi | Kosdaq | Wti | Usdkrw | Silver | Gold | Gbond3y | Chf | Aud | Usdidx

async def _save_one_collection(collection_name: str, data: T, client: AsyncIOMotorClient):
    """단일 컬렉션에 대해 날짜 기준으로 문서 저장."""
    try:
        coll = get_collection(client, DB_NAME, collection_name)
        await coll.create_index([("날짜", DESCENDING),], unique=True)

        # 날짜 값을 UTC 기준으로 변환
        utc_day = data.날짜.astimezone(timezone.utc)
        start_of_day = datetime.combine(utc_day.date(), time.min, tzinfo=timezone.utc)

        # 문서 변환
        doc = data.model_dump(by_alias=True, mode="python")
        doc["날짜"] = start_of_day  # 정확한 날짜 기준으로 덮어쓰기

        # upsert 수행
        result = await coll.replace_one(
            {"날짜": start_of_day},
            doc,
            upsert=True
        )

        status = "inserted" if result.upserted_id else "updated"
        return {
            "status": status,
            "_id": str(result.upserted_id) if result.upserted_id else "replaced"
        }

    except Exception as e:
        mylogger.exception(f"{collection_name}: 저장 중 오류 발생")
        return {"status": "error", "reason": str(e)}


async def find(col: str, date_str: str, client: AsyncIOMotorClient):
    collection = get_collection(client, DB_NAME, col)
    date_obj = datetime.strptime(date_str, DATE_FORMAT)
    doc = await collection.find_one({"날짜": date_obj})
    mylogger.debug(f"{col} 날짜 타입 확인:", doc["날짜"], repr(doc["날짜"]))
    if doc:
        print(f"조회 결과 ({col}): {doc}")
    else:
        print(f"{col} 컬렉션에 {date_str} 날짜 데이터 없음")


async def delete(col: str, date_str: str, client: AsyncIOMotorClient):
    collection = get_collection(client, DB_NAME, col)
    date_obj = datetime.strptime(date_str, DATE_FORMAT)
    result = await collection.delete_one({"날짜": date_obj})
    if result.deleted_count > 0:
        print(f"{col}: {date_str} 데이터 삭제 완료")
    else:
        print(f"{col}: 삭제할 데이터 없음")

MARKET = Literal["sp500", "kospi", "kosdaq", "wti", "usdkrw", "silver", "gold", "gbond3y", "chf", "aud"]

async def _save_market_history_type1(df: pd.DataFrame, market: MARKET, numeric_columns: list | None, client: AsyncIOMotorClient):
    MAP = {
        "sp500": Sp500,
        "kospi": Kospi,
        "kosdaq": Kosdaq,
        "wti": Wti,
        "usdkrw": Usdkrw,
        "silver": Silver,
        "gold": Gold,
        "gbond3y": Gbond3y,
        "chf": Chf,
        "aud": Aud,
    }
    if df.empty:
        print("빈 데이터프레임입니다.")
        return {"inserted": 0, "updated": 0}

    db = client[DB_NAME]
    coll = db[market]

    # 컬럼 정리
    df.columns = df.columns.str.strip()

    # 날짜 파싱
    try:
        df["날짜"] = pd.to_datetime(df["날짜"], format=DATE_FORMAT, utc=True)
    except Exception as e:
        print(f"날짜 파싱 실패: {e}")
        return {"inserted": 0, "updated": 0}

    # 숫자형 변환
    if numeric_columns:
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

    # dict 변환
    records = df.to_dict(orient="records")
    await coll.create_index([("날짜", DESCENDING),], unique=True)

    # upsert 준비
    operations = []
    for r in records:
        if "날짜" not in r:
            print("날짜 필드 없음 - 건너뜀:", r)
            continue
        item:T = MAP[market](**r)
        doc = item.model_dump(by_alias=True, mode="python")
        operations.append(UpdateOne({"날짜": item.날짜}, {"$set": doc}, upsert=True))

    # 실행
    if operations:
        result = await coll.bulk_write(operations)
        print(f"{market}: upsert 완료 - 삽입 {result.upserted_count}, 수정 {result.modified_count}")
        return {"inserted": result.upserted_count, "updated": result.modified_count}
    else:
        print("실행할 작업이 없습니다.")
        return {"inserted": 0, "updated": 0}

