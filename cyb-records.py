"""
Stats
"""

import pyodbc
import sys
import os

class Record(object):
    """Represents a record."""

class Machine(Record): 
    """Represents a machine."""

class Event(Record):
    """Represents a thrown Event."""

class Facility(Record):
    """Represents a facility where a machine is located"""

class Stat(Record):
    """Represents a statistic"""

class Table(object):
    """Represents a table as a list of objects"""

    def __init__(self):
        self.records = []
        
    def __len__(self):
        return len(self.records)

    def ReadDatabase(self, fields, constructor):
        """Reads a compressed data file builds one object per record.

        Args:
            data_dir: string directory name
            filename: string name of the file to read

            fields: sequence of (name, start, end, case) tuples specifying 
            the fields to extract

            constructor: what kind of object to create
        """

        """Connect to server"""
        cnxn = pyodbc.connect('DRIVER={SQL Server}; SERVER=medtweb2; DATABASE=MachineData; UID=username; PWD=password')
        cursor = cnxn.cursor()

        """Select correct table"""
        if constructor.__name__ == "Facility":
            table = "facilities"
        elif constructor.__name__ == "Machine":
            table = "current_system_infos"
        elif constructor.__name__ == "Event":
            table = "event_infos"
        elif constructor.__name__ == "Stat":
            table = "stats"

        """Grab some data using SQL"""
        cursor.execute("SELECT * from "+table+"")
        rows = cursor.fetchall()

        for row in rows:
            record = self.MakeRecord(row, fields, constructor)
            self.AddRecord(record)

    def MakeRecord(self, row, fields, constructor):
        """Scans a row and returns an object with the appropriate fields.

        Args:
            fields: sequence of (name, start, end, cast) tuples specifying 
            the fields to extract

            constructor: callable that makes an object for the record.

        Returns:
            Record with appropriate fields.
        """
        obj = constructor()

        for field in fields:
            val = getattr(row, field)   #from the row attribute, get the field
            setattr(obj, field, val)    #take value from row, set for new record created
        return obj

    def AddRecord(self, record):
        """Adds a record to this table.

        Args:
            record: an object of one of the record types.
        """
        self.records.append(record)

    def ExtendRecords(self, records):
        """Adds records to this table.

        Args:
            records: a sequence of record object
        """
        self.records.extend(records)

    def Recode(self):
        """Child classes can override this to recode values."""
        pass

class Machines(Table):
    """Represents the machine table."""

    def ReadRecords(self):
        self.ReadDatabase(self.GetFields(), Machine)

    def GetFields(self):
        """Returns a tuple specifying the fields to extract.

        The elements of the tuple are field, start, end, case.

                field is the name of the variable
                start and end are the indices as specified in the NSFG docs
                cast is a callable that converts the result to int, float, etc.
        """
        return [
            "id", "sn", "product_number", "product_configuration", "product_year", "product_month", "product_day", "product_daily_series", "product_medical", "facility_id", "sgfx_svn", "led_sw_rev", "led_svn", "epem_minor_rev", "epem_major_rev", "mcc_sw_rev", "motor_rev", "mcc_model", "sgfx_sw_rev", "mcc_svn", "created_at", "received_at"
            ] #just remove fields you don't need

def main():
    mach = Machines()
    mach.ReadRecords()
    print 'Number of machines', len(mach.records)
    
if __name__ == '__main__':
    main()