import pandas as pd
import re
import json

''' 
def clean_metadata(file_name, new_file_name):
//clean_abbrev(abbrev)

'''

# Function to clean abbreviations
def clean_abbrev(abbrev):
    '''
    given the detail in census data and clean it up to make a abbreviation 

    :param abbrev: the abbreviation to clean
    :return: cleaned abbreviation
    '''
    words = abbrev.split('_')

    # Replace 'percent' with 'pct' and other with 'est'

    ## if the first word *contains* 'percent'
    if words[0].find('percent') != -1:
        words[0] = 'pct'
    else:
        words[0] = 'est'

    # Remove non-letter characters except underscore
    words = [re.sub(r'[^\w\s]', '', word) for word in words]

    # Keep at most 3 words after the first word
    words = words[:4]

    # remove last word when it is hanging
    if words[-1] in ["and", "or", "no", "except", "excluding"]:
        words = words[:-1]

    return '_'.join(words)

def clean_metadata(file_name, new_file_name):
    '''
    clean the metadata file for acs5 us census data 
    the data is suppose to have 3 columns: "Category", "Code", "Detail"
    see sample file in the repo: census_metadata.xlsx

    :param file_name: the name of the file to clean
    :param new_file_name: the name of the new file to create
    '''
    with pd.ExcelFile(file_name) as xls:
        # Get sheet names
        sheet_names = xls.sheet_names

        # Create a new Excel writer object
        with pd.ExcelWriter(new_file_name, engine='openpyxl') as writer:
            # Loop over each sheet
            for sheet in sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet)

                # Add 'Abbrev' column
                df['Abbrev'] = df['Detail'].apply(lambda x: '_'.join([x.split('!!')[0].lower(),
                                                                    '_'.join(x.split('!!')[-1].lower().split())]))

                # Clean 'Abbrev' column
                df['Abbrev'] = df['Abbrev'].apply(clean_abbrev)

                # Check for duplicates in 'Abbrev'
                if df['Abbrev'].duplicated().any():
                    print(f'Duplicates found in sheet {sheet}')
                    # Append the last word from 'Detail' to the 'Abbrev' for duplicates
                    dup_rows = df[df['Abbrev'].duplicated(keep=False)]
                    for idx, row in dup_rows.iterrows():
                        df.loc[idx, 'Abbrev'] += "_" + row['Detail'].split('!!')[-1].split()[-1].lower()


                # Save each sheet to the new Excel file
                df.to_excel(writer, sheet_name=sheet, index=False)

    print('New Excel file successfully created.')

def generate_json_files(file_name):
    '''
    Generate 3 json files from the metadata file
    1. category_code.json: a dictionary of Category and Code relationships for each year
    2. year_category_abbrev.json: a dictionary of Year, Category and Abbrev relationships
    3. category_abbrev_shared.json: the shared Abbrevs across all years for each Category

    :param file_name: the name of the metadata file
    
    '''
    
    with pd.ExcelFile(file_name) as xls:
        # Get sheet names (representing years)
        sheet_names = xls.sheet_names

        # Read each sheet into a separate DataFrame
        all_data = {sheet: pd.read_excel(xls, sheet_name=sheet) for sheet in sheet_names}

    # Create a dictionary to store Category and Code relationships for each year
    category_code_dict = {}

    # Create a dictionary to store Year, Category and Abbrev relationships
    year_category_abbrev_dict = {}

    for sheet in sheet_names:
        # Extract Category, Code and Abbrev from the current DataFrame
        for idx, row in all_data[sheet].iterrows():
            # Update category_code_dict
            if row['Category'] not in category_code_dict:
                category_code_dict[row['Category']] = {sheet: [row['Code']]}
            else:
                if sheet not in category_code_dict[row['Category']]:
                    category_code_dict[row['Category']][sheet] = [row['Code']]
                else:
                    category_code_dict[row['Category']][sheet].append(row['Code'])

            # Update year_category_abbrev_dict
            if sheet not in year_category_abbrev_dict:
                year_category_abbrev_dict[sheet] = {row['Category']: [row['Abbrev']]}
            else:
                if row['Category'] not in year_category_abbrev_dict[sheet]:
                    year_category_abbrev_dict[sheet][row['Category']] = [row['Abbrev']]
                else:
                    year_category_abbrev_dict[sheet][row['Category']].append(row['Abbrev'])

    # Write category_code_dict to a JSON file
    with open('category_code.json', 'w') as f:
        json.dump(category_code_dict, f, indent=4)

    # Write year_category_abbrev_dict to a JSON file
    with open('year_category_abbrev.json', 'w') as f:
        json.dump(year_category_abbrev_dict, f, indent=4)

        # Create a set for all shared Abbrevs
    shared_abbrevs = set(all_data[sheet_names[0]]['Abbrev'])

    # Find shared Abbrevs across all years
    for sheet in sheet_names[1:]:
        shared_abbrevs &= set(all_data[sheet]['Abbrev'])

    # Create a dictionary to store Category and Abbrev relationships
    category_abbrev_dict = {}

    # Only consider shared Abbrevs
    for sheet in sheet_names:
        for idx, row in all_data[sheet].iterrows():
            if row['Abbrev'] in shared_abbrevs:
                if row['Category'] in category_abbrev_dict:
                    if row['Abbrev'] not in category_abbrev_dict[row['Category']]:
                        category_abbrev_dict[row['Category']].append(row['Abbrev'])
                else:
                    category_abbrev_dict[row['Category']] = [row['Abbrev']]

    # Write to a JSON file
    with open('category_abbrev_shared.json', 'w') as f:
        json.dump(category_abbrev_dict, f, indent=4)

def main():

    clean_metadata('census_metadata.xlsx', 'census_metadata_cleaned.xlsx')
    generate_json_files('census_metadata_cleaned.xlsx')

if __name__ == '__main__':
    main()
