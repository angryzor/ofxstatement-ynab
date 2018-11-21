from ofxstatement.plugin import Plugin
from ofxstatement.parser import CsvStatementParser
from ofxstatement.statement import StatementLine
from ofxstatement.exceptions import ParseError
import csv
import re

HEADER_START = "Account"

amount_exp = re.compile("\d+\.\d+")

class YNABPlugin(Plugin):
    """Belgian Belfius Bank plugin for ofxstatement
    """

    def get_parser(self, filename):
        f = open(filename, 'r')
        parser = YNABParser(f)
        return parser


class YNABParser(CsvStatementParser):

    date_format = "%Y-%m-%d"

    mappings = {
        'date': 2,
        'memo': 7,
        'payee': 3,
    }

    def split_records(self):
        """Return iterable object consisting of a line per transaction
        """
        return csv.reader(self.fin, delimiter=',')

    def parse_record(self, line):
        """Parse given transaction line and return StatementLine object
        """
        if line[0] == HEADER_START:
            return None

        # Check the account id. Each line should be for the same account!
        if self.statement.account_id:
            if line[0] != self.statement.account_id:
                raise ParseError(self.line_nr,
                                 'AccountID does not match on all lines! ' +
                                 'Line has ' + line[0] + ' but file ' +
                                 'started with ' + self.statement.account_id)
        else:
            self.statement.account_id = line[0]

        stmt_ln = super(YNABParser, self).parse_record(line)

        stmt_ln.amount = self.parse_value(amount_exp.search(line[8])[0], 'amount') - self.parse_value(amount_exp.search(line[9])[0], 'amount')

        return stmt_ln
