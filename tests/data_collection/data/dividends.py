DIVIDENDS_0 = """
{
  "dividends": {
    "metadata": {
      "secid": {
        "type": "string",
        "bytes": 36,
        "max_size": 0
      },
      "isin": {
        "type": "string",
        "bytes": 36,
        "max_size": 0
      },
      "registryclosedate": {
        "type": "date",
        "bytes": 10,
        "max_size": 0
      },
      "value": {
        "type": "double"
      },
      "currencyid": {
        "type": "string",
        "bytes": 9,
        "max_size": 0
      }
    },
    "columns": [
      "secid",
      "isin",
      "registryclosedate",
      "value",
      "currencyid"
    ],
    "data": [
      [
        "SBER",
        "RU0009029540",
        "2019-06-13",
        16, "RUB"
      ]  
    ]
  }
}
"""
DIVIDENDS_1 = """
{
  "dividends": {
    "metadata": {
      "secid": {
        "type": "string",
        "bytes": 36,
        "max_size": 0
      },
      "isin": {
        "type": "string",
        "bytes": 36,
        "max_size": 0
      },
      "registryclosedate": {
        "type": "date",
        "bytes": 10,
        "max_size": 0
      },
      "value": {
        "type": "double"
      },
      "currencyid": {
        "type": "string",
        "bytes": 9,
        "max_size": 0
      }
    },
    "columns": [
      "secid",
      "isin",
      "registryclosedate",
      "value",
      "currencyid"
    ],
    "data": [
      [
        "SBER",
        "RU0009029540",
        "2019-06-13",
        16, "RUB"
      ],
      [
        "SBER",
        "RU0009029540",
        "2020-10-05",
        18.7, "RUB"
      ],
      [
        "SBER",
        "RU0009029540",
        "2021-05-12",
        18.7, "RUB"
      ]
    ]
  }
}
"""

DIVIDENDS_0_capture = '[]\n'
DIVIDENDS_1_capture = '[(2021-05-12, SBER, 18.7)]\n'
