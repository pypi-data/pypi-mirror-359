from .._req_builder import _list_dataitem
from ..._prismcomponent.prismcomponent import _PrismComponent, _PrismDataComponent
from ..._utils import _validate_args, _get_params
from ..._common import const

__all__ = ['summary', 'earnings_call', 'dataitems']


_data_category = __name__.split(".")[-1]


class _PrismEventComponent(_PrismDataComponent):
    _component_category_repr = _data_category

    @classmethod
    def _dataitems(cls, search: str = None, package: str = None):
        return _list_dataitem(
            datacategoryid=cls.categoryid,
            datacomponentid=cls.componentid,
            search=search,
            package=package,
        )


class summary(_PrismEventComponent):
    """
    | Short summary of a news data for a specific event type
    | Default frequency is aperiodic.

    Parameters
    ----------
        dataitemid : int
            | Unique identifier for the different data item. This identifies the type of the event (Analyst/Investor Day, Strategic Alliances, etc.)

        datetype : str, {'entereddate', 'announceddate'}, default 'entereddate'
            | Datetype determines which date is fetched.

            - entereddate: when news data is inserted to the database
            - announceddate: when news data is announced

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> di = ps.event.dataitems()
        >>> di[["dataitemid", "dataitemname"]]
           dataitemid                                  dataitemname
        0      400001                               Address Changes
        1      400002                          Analyst/Investor Day
        2      400003  Announcement of Interim Management Statement
        3      400004             Announcement of Operating Results
        4      400005                     Announcements of Earnings
        ...       ...                                           ...
        156    400157                         Stock Dividends (<5%)
        157    400158    Stock Splits & Significant Stock Dividends
        158    400159                           Strategic Alliances
        159    400160                 Structured Products Offerings
        160    400161                                Ticker Changes

        >>> summ = ps.event.summary(dataitemid=400005)
        >>> summ_df = summ.get_data(universe="S&P 500", startdate="2010-01-01", enddate="2015-12-31", shownid=["Company Name"])
        >>> summ_df
               listingid                 date                                           headline                                            content                 Company Name
        0        2588294  2010-04-28 22:51:00  The Allstate Corporation Reports Earnings Resu...  The Allstate Corporation reported earnings res...                ALLSTATE CORP
        1        2588294  2010-02-11 00:55:00  Allstate Corp. Reports Earnings Results for th...  Allstate Corp. reported earnings results for t...                ALLSTATE CORP
        2        2588294  2010-04-28 22:40:00  The Allstate Corporation Reports Earnings Resu...  The Allstate Corporation reported earnings res...                ALLSTATE CORP
        3        2588294  2010-10-27 23:36:00  The Allstate Corporation Reports Unaudited Con...  The Allstate Corporation reported unaudited co...                ALLSTATE CORP
        4        2588294  2011-08-02 00:09:00  Allstate Corp. Reports Earnings Results for th...  Allstate Corp. reported earnings results for t...                ALLSTATE CORP
        ...          ...                  ...                                                ...                                                ...                          ...
        13056  302980253  2015-10-20 00:03:00  NiSource Gas Transmission & Storage Company Re...  NiSource Gas Transmission & Storage Company re...  COLUMBIA PIPELINE GROUP INC
        13057  302980253  2015-10-20 00:03:00  NiSource Gas Transmission & Storage Company An...  NiSource Gas Transmission & Storage Company an...  COLUMBIA PIPELINE GROUP INC
        13058  302980253  2015-10-20 00:03:00  NiSource Gas Transmission & Storage Company Re...  NiSource Gas Transmission & Storage Company re...  COLUMBIA PIPELINE GROUP INC
        13059  302980253  2015-11-03 07:42:00  Columbia Pipeline Group, Inc. Announces Unaudi...  Columbia Pipeline Group, Inc. announced unaudi...  COLUMBIA PIPELINE GROUP INC
        13060  316754620  2015-12-02 21:26:00  Computer Sciences GS Business Reports Unaudite...  Computer Sciences GS Business reported unaudit...                     CSRA INC
    """
    @_validate_args
    def __init__(
        self,
        dataitemid: int,
        datetype: const.DateType = 'entereddate',
    ):
        super().__init__(**_get_params(vars()))

    @classmethod
    @_validate_args
    def dataitems(cls, search: str = None, package: str = None):
        """
        Usable data items for the news data component.

        Parameters
        ----------
            search : str, default None
                | Search word for dataitems name, the search is case-insensitive.

            package : str, default None
                | Search word for package name, the search is case-insensitive.

        Returns
        -------
            pandas.DataFrame
                Data items that belong to cash flow statement data component.

            Columns:
                - *datamodule*
                - *datacomponent*
                - *dataitemid*
                - *datadescription*


        Examples
        --------
            >>> di = ps.event.summary.dataitems()
            >>> di[["dataitemid", "dataitemname"]]
            dataitemid                                  dataitemname
            0      400001                               Address Changes
            1      400002                          Analyst/Investor Day
            2      400003  Announcement of Interim Management Statement
            3      400004             Announcement of Operating Results
            4      400005                     Announcements of Earnings
            ...       ...                                           ...
            156    400157                         Stock Dividends (<5%)
            157    400158    Stock Splits & Significant Stock Dividends
            158    400159                           Strategic Alliances
            159    400160                 Structured Products Offerings
            160    400161                                Ticker Changes
        """
        return cls._dataitems(search=search, package=package)


class economics(_PrismEventComponent):
    """
    | Data that pertains to building an economic calendar.
    | Default frequency is aperiodic daily.

    Parameters
    ----------
            package : str {'LSEG Street Events'}
                | Desired data package in where the pricing data outputs from.

                .. admonition:: Warning
                    :class: warning

                    If an invalid package is entered without a license, an error will be generated as output.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------

        >>> economic_calendar = ps.event.economics()
        >>> economic_calendar_df = economic_calendar.get_data(startdate='2025-01-01')
        Data preparation complete
        Downloading: 100%|██████████| 327k/327k [00:00<00:00, 92.7MB/s]

        >>> economic_calendar_df
        Out[15]:
                             date releasedfor  seqnum  ... actual consensus unit
        0     2025-01-01 00:00:00   Dec. 2024       1  ...    6.6         4    %
        1     2025-01-01 00:00:00   Dec. 2024       2  ...    6.6         4    %
        2     2025-01-01 00:00:00   Dec. 2024       3  ...    6.6       3.1    %
        3     2025-01-01 00:00:00   Dec. 2024       4  ...    6.6         4    %
        4     2025-01-01 00:00:00   Dec. 2024       5  ...    6.6         4    %
        ...                   ...         ...     ...  ...    ...       ...  ...
        50697 2033-02-07 04:00:00        2032       1  ...   None      None    %
        50698 2034-02-06 04:00:00        2033       1  ...   None      None    %
        50699 2035-02-05 04:00:00        2034       1  ...   None      None    %
        50700 2036-02-05 04:00:00        2035       1  ...   None      None    %
        50701 2037-02-05 04:00:00        2036       1  ...   None      None    %
        [50702 rows x 9 columns]

    """
    @_validate_args
    def __init__(self, package: str = None):
        super().__init__(**_get_params(vars()))


class events(_PrismEventComponent):
    """
    | Data pertaining to company's events
    | Default frequency is aperiodic daily.

    Parameters
    ----------
            package : str {'LSEG Street Events'}
                | Desired data package in where the pricing data outputs from.

                .. admonition:: Warning
                    :class: warning

                    If an invalid package is entered without a license, an error will be generated as output.

    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> events = ps.event.events()
        >>> events_df = events.get_data("S&P 500",startdate='2025-01-01')
        Data preparation complete
        Downloading: 100%|██████████| 214k/214k [00:00<00:00, 42.0MB/s]

        >>> events_df
        Out[17]:
              listingid  ...                              event_type
        0         21580  ...  Earnings Conference Call/ Presentation
        1         21580  ...                             Ex-Dividend
        2         21580  ...                        Earnings Release
        3         21580  ...                             Ex-Dividend
        4         21580  ...             Shareholders Annual Meeting
        ...         ...  ...                                     ...
        6454    3237047  ...             Shareholders Annual Meeting
        6455    3237047  ...  Earnings Conference Call/ Presentation
        6456    3237047  ...                 Conference Presentation
        6457    3237047  ...                        Earnings Release
        6458    3237047  ...                 Conference Presentation
        [6459 rows x 10 columns]
    """
    @_validate_args
    def __init__(self, package: str = None):
        super().__init__(**_get_params(vars()))

class earnings(_PrismEventComponent):
    """
    | Data that pertains to building an earnings calendar.
    | Default frequency is aperiodic daily.

    Parameters
    ----------
        period_type : str, {'A', 'Q'}
            | Financial Period in which the financial statement results are reported.
            | A Financial Period can be of one of the following Period Types:

            - Annual period (A)
            - Quarterly period (Q)

        package : str {'LSEG Street Events'}
            | Desired data package in where the pricing data outputs from.

            .. admonition:: Warning
                :class: warning

                If an invalid package is entered without a license, an error will be generated as output.


    Returns
    -------
        prismstudio._PrismComponent

    Examples
    --------
        >>> earnings_calendar = ps.event.earnings(period_type='Q')
        >>> earnings_calendar_df = earnings_calendar.get_data(startdate='2025-01-01', shownid=['MIC', 'RIC'])
        Data preparation complete
        Downloading: 100%|██████████| 321k/321k [00:00<00:00, 169MB/s]

        >>> earnings_calendar_df
        Out[13]:
               listingid period_enddate calendar_period  ... brokers   MIC      RIC
        0           8875     2025-01-31          2024Q4  ...    13.0  XMAD   ITX.MC
        1          14322     2025-01-31          2024Q4  ...    12.0  XTKS   1928.T
        2          14989     2025-01-31          2024Q4  ...     NaN  XTKS   4996.T
        3          15886     2025-01-31          2024Q4  ...     4.0  XTKS   6966.T
        4          16248     2025-01-31          2024Q4  ...     NaN  XTKS   8013.T
        ...          ...            ...             ...  ...     ...   ...      ...
        24399    3715969     2025-09-30          2025Q3  ...     2.0  XNCM  ISBA.OQ
        24400    3717037     2025-09-30          2025Q3  ...     2.0  XNGS  STRZ.OQ
        24401    3717483     2025-09-30          2025Q3  ...    14.0  XNGS  ETOR.OQ
        24402    3720442     2025-09-30          2025Q3  ...     7.0  XNYS   MNTN.N
        24403    3733833     2025-09-30          2025Q3  ...     1.0  XASE    AIM.A
        [24404 rows x 9 columns]
    """
    @_validate_args
    def __init__(self, period_type: str, package: str = None, ):
        super().__init__(**_get_params(vars()))


class earnings_call(_PrismEventComponent):
    """
        | Transcript of the earnings conference call
        | Default frequency is aperiodic.

        Parameters
        ----------
            package : str {'CIQ Transcripts', 'LSEG Transcripts & Briefs'}
                | Desired data package in where the pricing data outputs from.

                .. admonition:: Warning
                    :class: warning

                    If an invalid package is entered without a license, an error will be generated as output.

        Returns
        -------
            prismstudio._PrismComponent

        Examples
        --------
            >>> ec = ps.event.earnings_call()
            >>> ec_df = ec.get_data(universe="S&P 500", startdate="2020-01-01")
            >>> ec_df

            listingid  ...                                                    content
            0          111305  ...                            Tim Long with Barclays.
            1          111305  ...                    Matt Niknam with Deutsche Bank.
            2          111305  ...  Thanks, Sami, and thank you all for joining us...
            3          111305  ...  Thanks, Chuck. Our Q2 results reflect solid ex...
            4          111305  ...  Thank you, Scott. [Operator Instructions] Oper...
            ...           ...  ...                                                ...
            109232     901902  ...  And Julian, I would just add where we are, it'...
            109233     901902  ...  Michael, thank you. Everyone, we're excited ab...
            109234     901902  ...  Yes. I appreciate you squeezing me in here. I ...
            109235     901902  ...  Chris, I appreciate the question. I mean there...
            109236     901902  ...  Operator, before we wrap up, let me turn it ba...
    """
    @_validate_args
    def __init__(self, package: str = None):
        super().__init__(**_get_params(vars()))


def dataitems(search: str = None, package: str = None):
    """
    Usable data items for the event data category.

    Parameters
    ----------
        search : str, default None
            | Search word for dataitems name, the search is case-insensitive.

        package : str, default None
            | Search word for package name, the search is case-insensitive.

    Returns
    -------
        pandas.DataFrame
            Data items that belong to cash flow statement data component.

        Columns:
            - *datamodule*
            - *datacomponent*
            - *dataitemid*
            - *datadescription*


    Examples
    --------
        >>> di = ps.event.dataitems()
        >>> di[["dataitemid", "dataitemname"]]
           dataitemid                                  dataitemname
        0      400001                               Address Changes
        1      400002                          Analyst/Investor Day
        2      400003  Announcement of Interim Management Statement
        3      400004             Announcement of Operating Results
        4      400005                     Announcements of Earnings
        ...       ...                                           ...
        156    400157                         Stock Dividends (<5%)
        157    400158    Stock Splits & Significant Stock Dividends
        158    400159                           Strategic Alliances
        159    400160                 Structured Products Offerings
        160    400161                                Ticker Changes
    """
    return _list_dataitem(
        datacategoryid=_PrismEventComponent.categoryid,
        datacomponentid=None,
        search=search,
        package=package,
    )
