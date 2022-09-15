"""
Name:    shareholding.py
Author:  kyh
Created: 9/15/2022 11:01 PM
"""
import datetime
from urllib import parse, request

import pandas as pd
import requests
from bs4 import BeautifulSoup

from utils import get_logger

logger = get_logger(name=__file__)


class ShareHolding:
    Date = "Date"

    ParticipantID = "Participant ID"
    ParticipantName = "Participant Name"
    Shareholding = "Shareholding"
    ShareholdingPct = "Shareholding Percent"

    SOURCE_MAP = {
        ParticipantID: "col-participant-id",
        ParticipantName: "col-participant-name",
        Shareholding: "col-shareholding text-right",
        ShareholdingPct: "col-shareholding-percent text-right"
    }
    PROCESS_MAP = {
        Shareholding: lambda v: v.replace(",", ""),
        ShareholdingPct: lambda v: float(v.replace("%", "")) / 100.0
    }
    DTYPE_MAP = {
        ParticipantID: pd.StringDtype(),
        ParticipantName: pd.StringDtype(),
        Shareholding: pd.Int64Dtype(),
        ShareholdingPct: pd.Float64Dtype()
    }


class ShareHoldingDAO:
    SOURCE_URL = "https://www3.hkexnews.hk/sdw/search/searchsdw.aspx"
    MARKUP = "lxml"

    __PAYLOAD = {
        # Fixed
        '__EVENTTARGET': "btnSearch",
        '__EVENTARGUMENT': "",
        'sortBy': "shareholding",
        'sortDirection': "desc",
        # To be filled at __init__
        '__VIEWSTATE': "",
        '__VIEWSTATEGEN': "",
        'today': "",
        # To be filled dynamically
        # Must-haves
        # txtShareholdingDate
        # txtStockCode
        # Filters
        # txtParticipantID
        # txtParticipantName
    }

    def __init__(self):
        page = requests.get(self.SOURCE_URL)
        soup = BeautifulSoup(page.text, self.MARKUP)

        self.__PAYLOAD['__VIEWSTATE'] = soup.select("#__VIEWSTATE")[0]['value']
        self.__PAYLOAD['__VIEWSTATEGEN'] = soup.select("#__VIEWSTATEGENERATOR")[0]['value']
        self.__PAYLOAD['today'] = datetime.date.today().strftime("%Y%m%d")

    def __payload(self, date: datetime.date, stockcode: str,
                  participant_id: str = "", participant_name: str = "") -> bytes:
        payload = self.__PAYLOAD.copy()

        payload['txtShareholdingDate'] = date.strftime("%Y/%m/%d")
        payload['txtStockCode'] = stockcode

        if participant_id:
            payload['txtParticipantID'] = participant_id
        if participant_name:
            payload['txtParticipantName'] = participant_name

        return parse.urlencode(payload).encode()

    @staticmethod
    def __process_row(row, column):
        func = ShareHolding.PROCESS_MAP.get(column) or (lambda v: v)
        return func(row.find("td", class_=ShareHolding.SOURCE_MAP[column]).find("div", class_="mobile-list-body").text)

    def get_data_by_stock(self, stockcode: str, date: datetime.date,
                          columns=None, top_n=None):
        logger.info(f"Fetching shareholding data for {stockcode} on {date} (source: {self.SOURCE_URL})")
        data = []
        columns = columns or ShareHolding.DTYPE_MAP.keys()
        dtypes = {k: v for k, v in ShareHolding.DTYPE_MAP.items() if k in columns}

        req = request.Request(self.SOURCE_URL, data=self.__payload(date, stockcode))
        resp = request.urlopen(req)
        soup = BeautifulSoup(resp, self.MARKUP)

        try:
            rows = soup.find("table").find("tbody").find_all("tr", limit=top_n)
            for row in rows:
                data.append((date, *[self.__process_row(row, column) for column in columns]))
            logger.info(f"Fetched shareholding data for {stockcode} on {date}, totaling {len(data)} rows")
        except Exception as e:
            logger.exception(e)

        df = pd.DataFrame(data, columns=[ShareHolding.Date, *columns])
        df[ShareHolding.Date] = pd.to_datetime(df[ShareHolding.Date], format="%Y-%m-%d")
        return df.astype(dtypes)


if __name__ == "__main__":
    from dateutil.relativedelta import relativedelta

    dao = ShareHoldingDAO()
    df = dao.get_data_by_stock("00700", date=datetime.date.today() + relativedelta(days=-1), top_n=10)
    logger.info("\n" + df.to_string())
