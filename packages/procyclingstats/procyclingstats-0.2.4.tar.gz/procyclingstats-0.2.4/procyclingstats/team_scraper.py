from typing import Any, Dict, List, Optional

from .scraper import Scraper
from .table_parser import TableParser
from .utils import (get_day_month, join_tables, parse_select,
                    parse_table_fields_args)


class Team(Scraper):
    """
    Scraper for team HTML page.

    Usage:

    >>> from procyclingstats import Team
    >>> team = Team("team/bora-hansgrohe-2022")
    >>> team.abbreviation()
    'BOH'
    >>> team.parse()
    {
        'abbreviation': 'BOH',
        'bike': 'Specialized',
        'history_select': [
            {
                'text': '2027 | BORA - hansgrohe',
                'value': 'team/bora-hansgrohe-2027/overview/'
            },
            ...
        ],
        'name': 'BORA - hansgrohe',
        ...
    }
    """
    def name(self) -> str:
        """
        Parses team display name from HTML.

        :return: Display name, e.g. ``BORA - hansgrohe``.
        """
        display_name_html = self.html.css_first(".page-title h1")
        return display_name_html.text().split(" (")[0]

    def nationality(self) -> str:
        """
        Parses team's nationality from HTML.

        :return: Team's nationality as 2 chars long country code in uppercase.
        """
        nationality_html = self.html.css_first(
            ".page-title span.flag")
        flag_class = nationality_html.attributes['class']
        return flag_class.split(" ")[1].upper() # type: ignore

    def status(self) -> str:
        """
        Parses team status (class) from HTML.

        :return: Team status as 2 chars long code in uppercase, e.g. ``WT``.
        """
        team_status_html = self.html.css_first(
            "div > ul.infolist > li:nth-child(1) > div:nth-child(2)")
        return team_status_html.text()

    def abbreviation(self) -> str:
        """
        Parses team abbreviation from HTML.

        :return: Team abbreviation as 3 chars long code in uppercase, e.g.
            ``BOH``
        """
        abbreviation_html = self.html.css_first(
            "div > ul.infolist > li:nth-child(2) > div:nth-child(2)")
        return abbreviation_html.text()

    def bike(self) -> str:
        """
        Parses team's bike brand from HTML.

        :return: Bike brand e.g. ``Specialized``.
        """
        bike_html = self.html.css_first(
            "div > ul.infolist > li:nth-child(4) > div:nth-child(2)")
        return bike_html.text()
    
    def _parse_team_stat(self, stat_name: str) -> Optional[int]:
        """
        Helper to parse a team's statistic from the HTML by the stat's label.

        :param stat_name: Label text to search for (e.g. "Victories", "Points").
        :return: Integer value of the stat or None if not found.
        """
        for li in self.html.css("ul.teamkpi > li"):
            font_el = li.css_first("div.title")
            if font_el and font_el.text().strip() == stat_name:
                a_el = li.css_first("div.value > a")
                if a_el:
                    value = a_el.text().strip()
                    if value.isdigit():
                        return int(value)
                    elif value == "-":
                        return 0
        return None

    def wins_count(self) -> Optional[int]:
        """
        Parses count of wins in corresponding season from HTML.

        :return: Count of wins in corresponding season.
        """
        return self._parse_team_stat("Victories")
    
    def pcs_points(self) -> Optional[int]:
        """
        Parses team's PCS points from HTML.

        :return: PCS points gained throughout corresponding year.
        """
        return self._parse_team_stat("Points")
   

    def pcs_ranking_position(self) -> Optional[int]:
        """
        Parses team's PCS ranking position from HTML.

        :return: PCS team ranking position in corresponding year.
        """
        return self._parse_team_stat("PCS#")
        
    def uci_ranking_position(self) -> Optional[int]:
        """
        Parses team's UCI ranking position from HTML.

        :return: UCI team ranking position in corresponding year.
        """
        return self._parse_team_stat("UCI#")
   

    def history_select(self) -> List[Dict[str, str]]:
        """
        Parses team seasons select menu from HTML.

        :return: Parsed select menu represented as list of dicts with keys
            ``text`` and ``value``.
        """
        team_seasons_select_html = self.html.css_first("form > select")
        return parse_select(team_seasons_select_html)

    def riders(self, *args: str) -> List[Dict[str, Any]]:
        """
        Parses team riders in curresponding season from HTML.

        :param args: Fields that should be contained in returned table. When
            no args are passed, all fields are parsed.

            - rider_name
            - rider_url
            - nationality: Rider's nationality as 2 chars long country code.
            - age: Rider's age.
            - since: First rider's day in the team in corresponding season in
              ``MM-DD`` format, most of the time ``01-01``.
            - until: Last rider's day in the team in corresponding season in
              ``MM-DD`` format, most of the time ``12-31``.
            - career_points: Current riders's career points.
            - ranking_points: Current rider's points in PCS ranking.
            - ranking_position: Current rider's position in PCS ranking.

        :raises ValueError: When one of args is of invalid value.
        :return: Table with wanted fields.
        """
        available_fields = (
            "nationality",
            "rider_name",
            "rider_url",
            "age",
            "since",
            "until",
            "career_points",
            "ranking_points",
            "ranking_position"
        )
        casual_fields = [
            "nationality",
            "rider_name",
            "rider_url"]
        fields = parse_table_fields_args(args, available_fields)
        career_points_table_html = self.html.css_first("div.points.riderlistcont table")
        table_parser = TableParser(career_points_table_html)
        career_points_fields = [field for field in fields
                         if field in casual_fields]
        # add rider_url to the table for table joining purposes
        if "rider_url" not in career_points_fields:
            career_points_fields.append("rider_url")
        table_parser.parse(career_points_fields)
        if "career_points" in fields:
            career_points = table_parser.parse_extra_column(2,
                lambda x: int(x) if x.isnumeric() else 0)
            table_parser.extend_table("career_points", career_points)
        table = table_parser.table

        # add ages to the table if needed
        if "age" in fields:
            ages_table_html = self.html.css_first("div.age.riderlistcont table")
            ages_tp = TableParser(ages_table_html)
            ages_tp.parse(["rider_url"])
            ages = ages_tp.parse_extra_column(2, lambda x: int(x[:2]) if x and x[:2].isdigit() else None)
            ages_tp.extend_table("age", ages)
            table = join_tables(table, ages_tp.table, "rider_url")

        # add ranking points and positions to the table if needed
        if "ranking_position" in fields or "ranking_points" in fields:
            ranking_table_html = self.html.css_first("div.ranking.riderlistcont table")
            ranking_tp = TableParser(ranking_table_html)
            ranking_tp.parse(["rider_url"])
            if "ranking_points" in fields:
                points = ranking_tp.parse_extra_column(2,
                    lambda x: int(x.replace("(", "").replace(")", ""))
                    if x.replace("(", "").replace(")", "").isnumeric() else 0)
                ranking_tp.extend_table("ranking_points", points)
            if "ranking_position" in fields:
                positions = ranking_tp.parse_extra_column(3,
                    lambda x: int(x) if x.isnumeric() else None)
                ranking_tp.extend_table("ranking_position", positions)
            table = join_tables(table, ranking_tp.table, "rider_url")

        # add rider's since and until dates to the table if needed
        if "since" in fields or "until" in fields:
            since_until_html_table = self.html.css_first("div.name.riderlistcont ul")
            since_tp = TableParser(since_until_html_table)
            since_tp.parse(["rider_url"])
            if "since" in fields:
                since_dates = since_tp.parse_extra_column(2,
                    lambda x: get_day_month(x) if "as from" in x else "01-01")
                since_tp.extend_table("since", since_dates)
            if "until" in fields:
                until_dates = since_tp.parse_extra_column(2,
                    lambda x: get_day_month(x) if "until" in x else "12-31")
                since_tp.extend_table("until", until_dates)
            table = join_tables(table, since_tp.table, "rider_url")

        # remove rider_url field if wasn't requested and was used for joining
        # tables only
        if "rider_url" not in fields:
            for row in table:
                row.pop("rider_url")
        return table
