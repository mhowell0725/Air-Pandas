import database_query as dbq
'''
A note for how to use each function in database_query.py
'''

def main():
    db_name = input("Please enter the name of the SQLite database: ")

    while True:
        print("\nSelect an option:")
        print("1. List all tables.")
        print("2. Get columns in a table.")
        print("3. Query a table.")
        print("4. Get unique FIPS codes.")
        print("5. Get unique sites.")
        print("6. Calculate poor air percentage.")
        print("7. Get air quality threshold percentages.")
        print("0. Exit.")
        option = int(input("Your choice: "))

        if option == 1:
            tables = dbq.get_all_tables(db_name)
            print("\nTables:")
            for table in tables:
                print(table)
        elif option == 2:
            table_name = input("\nEnter table name: ")
            columns = dbq.get_column_names(table_name, db_name)
            print("\nColumns:")
            for column in columns:
                print(column)
        elif option == 3:
            table_name = input("\nEnter table name: ")
            columns = input("Enter columns (comma separated): ").split(",")
            start_date = input("Enter start date: ")
            end_date = input("Enter end date: ")
            fips = input("Enter FIPS code (optional, leave empty to skip): ")
            fips = fips if fips else None
            df = dbq.query_table(db_name, table_name, columns, start_date, end_date, fips)
            print(df)
        elif option == 4:
            table_name = input("\nEnter table name: ")
            df = dbq.get_unique_fips(db_name, table_name)
            print(df)
        elif option == 5:
            table_name = input("\nEnter table name: ")
            df = dbq.get_unique_sites(db_name, table_name)
            print(df)
        elif option == 6:
            table_name = input("\nEnter table name: ")
            fips = input("Enter FIPS code: ")
            threshold = float(input("Enter threshold: "))
            start_date = input("Enter start date (optional, leave empty to skip): ")
            end_date = input("Enter end date (optional, leave empty to skip): ")
            start_date = start_date if start_date else None
            end_date = end_date if end_date else None
            percentage = dbq.get_poorair_percentage(db_name, table_name, fips, threshold, start_date, end_date)
            print(f"Percentage of poor air quality: {percentage}")
        elif option == 7:
            table_name = input("\nEnter table name: ")
            threshold = float(input("Enter threshold: "))
            df_counties = dbq.get_county_fips(db_name, table_name)
            df_percentages = dbq.air_threshold_percentages(df_counties, db_name, table_name, threshold)
            print(df_percentages)
        elif option == 0:
            print("\nExiting...")
            break
        else:
            print("\nInvalid option. Please try again.")

if __name__ == "__main__":
    main()
