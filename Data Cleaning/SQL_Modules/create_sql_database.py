import sql_utils
import pandas as pd
from sqlalchemy import create_engine


def main():
    ## Create a SQL engine -- the name of the database is 

    output_database_name = 'airpandas_1.sqlite' ## YOU CAN CHANGE THIS NAME
    engine = create_engine(f'sqlite:///{output_database_name}')

    
    census_file_name = {
        "Race" : r"database\census_data_RACE_2009-2021.csv",
        "Income" : r"database\census_data_INCOME_AND_BENEFITS_2009-2021.csv",
        "Education" : r"database\census_data_EDUCATIONAL_ATTAINMENT_2009-2021.csv",
        "Employment" : r"database\census_data_EMPLOYMENT_STATUS _2009-2021.csv",
        "Heating" : r"database\census_data_HOUSE_HEATING_FUEL _2009-2021.csv",
        "Occupation" : r"database\census_data_OCCUPATION_2009-2021.csv",
        "Commute" : r"database\census_data_COMMUTING_TO_WORK_2009-2021.csv",
        "Industry" : r"database\census_data_INDUSTRY_2009-2021.csv",
        "Poverty" : r"database\census_data_PERCENTAGE_OF_FAMILIES_AND_PEOPLE_WHOSE_INCOME_IN_THE_PAST_12_MONTHS_IS_BELOW_THE_POVERTY_LEVEL_2009-2021.csv",

    }

    for table_name, file_name in census_file_name.items():
        sql_utils.query_census(file_name, engine, table_name)

    file_names = [r'database\2009_2014.6_CA_PM2.5_samples.csv', r'database\2014.6_2021_CA_PM2.5_samples.csv']
    sql_utils.process_csv_in_chunks(file_names, 10000, engine, 'PM25')





if __name__ == '__main__':
    main()

