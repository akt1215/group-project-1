import csv

# ABSOLUTE PATH so it runs from VS Code terminal without changing folders- change if diffrent folders
AIR_PATH = "/Users/paolorfc/Desktop/INTRO TO COMPUTING/LECTURES/PROBLEMS/GROUPPROJECT1/air_quality.csv"
UHF_PATH = "/Users/paolorfc/Desktop/INTRO TO COMPUTING/LECTURES/PROBLEMS/GROUPPROJECT1/uhf.csv"

def make_record(geo_id_str, geo_desc, date_str, pm25_str):
    # (geo_id:int, geo_desc:str, date_str:str, pm25:float)
    return (int(geo_id_str), geo_desc, date_str, float(pm25_str))

# PART A (wrapped into a function, returns data in wanted form of dictionaries and a list of measurments for each type
def load_air_quality():
    measurements = []
    by_geo = {}   
    by_date = {}

    with open(AIR_PATH, 'r', encoding='utf-8-sig', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if not row or len(row) < 4:
                continue
            geo_id_str, geo_desc, date_str, pm25_str = row[:4]
            pm25 = float(pm25_str) 
            rec = make_record(geo_id_str, geo_desc, date_str, pm25)
            measurements.append(rec)

            g = int(geo_id_str)
            if g not in by_geo:
                by_geo[g] = []
            by_geo[g].append(rec)

            # build by_date without dict.get()
            if date_str not in by_date:
                by_date[date_str] = []
            by_date[date_str].append(rec)

    return measurements, by_geo, by_date


def split_to_uhf42_ids(version, id_str):
    """
    If version == 'UHF42': id_str is one 3-digit id (e.g., '105') -> [105]
    If version in {'UHF34','UHF35','UHF36'}: id_str is concatenated 3-digit ids
    (e.g., '105106107') -> split into ['105','106','107'] -> [105,106,107]
    """
    if version == "UHF42":
        return [int(id_str)]
    else:
        ids42 = []
        i = 0
        # chop into 3-char chunks and append to list
        while i < len(id_str):
            chunk = id_str[i:i+3]
            if chunk != "":
                ids42.append(int(chunk))
            i += 3
        return ids42
    


# If the version is UHF42, column 3 is a single 3-digit UHF ID (e.g., 101, 201, 305).

#Example from file: Bronx, UHF42, 101, 10463, 10471
#Borough = Bronx, UHF ID = 101, ZIPs = {10463, 10471}.

#If the version is UHF34 / UHF35 / UHF36, column 3 is a concatenation of multiple 3-digit UHF42 IDs (no commas).

#Example (UHF34) in file:
#Bronx, UHF34, 105106107, 10451, 10452, 10453, 10454, 10455, 10456, 10457, 10459, 10460, 10474
#→ This line represents three UHF42 areas: 105, 106, 107 that share those ZIPs.


def split_to_uhf42_ids(version, id_str):
    """
    Convert the version+id_str into a list of UHF42 integer IDs.
    - If version == 'UHF42': id_str is one 3-digit id (e.g., '105') -> [105]
    - If version in {'UHF34','UHF35','UHF36'}: id_str is concatenated 3-digit ids
      (e.g., '105106107') -> split into ['105','106','107'] -> [105,106,107]
    """
    if version == "UHF42":
        return [int(id_str)]
    else:
        ids42 = []
        i = 0
        # chop into 3-char chunks
        while i < len(id_str):
            chunk = id_str[i:i+3]
            if chunk != "":
                ids42.append(int(chunk))
            i += 3
        return ids42

def load_uhf_maps():
    """
    Read uhf.csv and build:
      - zip_to_uhf : zip(str) -> list of UHF42 ids (ints)
      - borough_to_uhf : borough(str) -> list of UHF42 ids (ints)
        avoid duplicates by checking 'if gid not in list'.
    
    """
    #gid refers to geo id
    zip_to_uhf = {}
    borough_to_uhf = {}

    with open(UHF_PATH, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 4:
                continue

            borough = row[0].strip()
            version = row[1].strip() #uhf version CHECK
            id_str  = row[2].strip()
            # remaining columns are ZIP codes (may include blanks)

           # append zips to list by iterating through them
            zips = []
            j = 3
            while j < len(row):
                z = row[j].strip()
                if z != "":
                    zips.append(z)
                j += 1

            # expand to UHF42 ints
            ids_42 = split_to_uhf42_ids(version, id_str)

            # update borough_to_uhf
            if borough not in borough_to_uhf:
                borough_to_uhf[borough] = []
               #following prevents duplicates 
            for gid in ids_42:
                if gid not in borough_to_uhf[borough]:
                    borough_to_uhf[borough].append(gid)

            # update zip_to_uhf
            for z in zips:
                if z not in zip_to_uhf:
                    zip_to_uhf[z] = []
                for gid in ids_42:
                    if gid not in zip_to_uhf[z]:
                        zip_to_uhf[z].append(gid)

    return zip_to_uhf, borough_to_uhf

#PART C-> query and print section

def print_results(rows):
    """
    Print each measurement in the requested format:
    <geo_id>, <geo_desc>, <date_str>, <pm2.5 with 2 decimals>
    """
    if not rows:
        print("No matching measurements.") #if no corresponsing thing
        return

    for (geo_id, geo_desc, date_str, pm25) in rows:
        # pm25 already float; print with 2 decimals
        print(f"{geo_id}, {geo_desc}, {date_str}, {pm25:.2f}")

#searching pm25 by zip

def search_by_zip(z, zip_to_uhf, by_geo):

    """A ZIP can belong to multiple UHF42 areas (because uhf.csv can list groups like UHF34/35/36 that expand to several 3-digit IDs).

      zip_to_uhf[z] gives you all those UHF42 IDs.

      by_geo[g] gives you all measurements for a specific UHF42 ID.

      Concatenating all by_geo[g] lists yields every measurement tied to that ZIP."""
    results = []  #create empty list to store result values
    if z in zip_to_uhf:   #check if z(input) exists as a key in zips to uhf 
        gids = zip_to_uhf[z]  # if z exists store all the UHF ids and store it in gids
        # gather all recs for each geo id
        i = 0
        while i < len(gids):  # loop over indices of gids
            g = gids[i] #call current uhf id g
            if g in by_geo:
                # extend results keeping original order
                recs = by_geo[g] #check if there is any measurment realted to g in by geo and if there is call the measurments recs
                k = 0
                while k < len(recs):
                    results.append(recs[k]) #append results of recs to results
                    k += 1
            i += 1. #movde to next uhf id
    return results
#after iterating through all uhf ids for the inputted zip return the results of measurments for each id



#function for searching by uhf id for each id returns a list of measurments
def search_by_uhf_id(g_str, by_geo):
    """UHF id (string from input) -> list of measurement tuples for that id."""
    try:
        g = int(g_str)
    except ValueError:
        return []  # invalid number
    if g in by_geo:
        # return a shallow copy so one doesn't change by_geo
        out = []
        recs = by_geo[g]
        i = 0
        while i < len(recs):
            out.append(recs[i])
            i += 1
        return out
    return []

#function for searching by borough

def search_by_borough(b, borough_to_uhf, by_geo):
    """Borough name (exact) -> collect all records from its UHF ids."""
    results = []
    if b in borough_to_uhf: #b is input
        gids = borough_to_uhf[b]
        i = 0
        while i < len(gids): #iterats through every uhf id
            g = gids[i]
            if g in by_geo:
                recs = by_geo[g]
                k = 0
                while k < len(recs):
                    results.append(recs[k])
                    k += 1 #gives measurment for each uhf id
            i += 1
    return results
        

#function for searching by date        
def search_by_date(d, by_date):
    """Exact date string (e.g., '6/1/09') -> list of tuples for that date."""
    if d in by_date:
        out = []
        recs = by_date[d]
        i = 0
        while i < len(recs):
            out.append(recs[i])
            i += 1
        return out
    return [] #measurmenrs for each id in each date


#user query section 

def query_loop(by_geo, by_date, zip_to_uhf, borough_to_uhf):

    while True:
        print("\nSearch by:")
        print("1 = ZIP")
        print("2 = UHF id")
        print("3 = Borough")
        print("4 = Date (m/d/yy)")
        print("q = Quit")
        choice = input("> ").strip().lower()
        #easy options for user

        if choice == "1":
            z = input("ZIP (5 digits): ").strip()
            rows = search_by_zip(z, zip_to_uhf, by_geo)
            print_results(rows)

        elif choice == "2":
            g = input("UHF id (3 digits): ").strip()
            rows = search_by_uhf_id(g, by_geo)
            print_results(rows)

        elif choice == "3":
            b = input("Borough (exact, e.g., Bronx): ").strip()
            rows = search_by_borough(b, borough_to_uhf, by_geo)
            print_results(rows)

        elif choice == "4":
            d = input("Date (m/d/yy, e.g., 6/1/09): ").strip()
            rows = search_by_date(d, by_date)
            print_results(rows)

        elif choice == "q":
            break

        else:
            print("Invalid option.")

def main():
    # Part (a)
    measurements, by_geo, by_date = load_air_quality()
    print("Loaded", len(measurements), "measurements.")
   
    # Part (b)
    zip_to_uhf, borough_to_uhf = load_uhf_maps()
    print("ZIPs mapped:", len(zip_to_uhf), "| Boroughs mapped:", len(borough_to_uhf))

    # Part (c): interactive search
    query_loop(by_geo, by_date, zip_to_uhf, borough_to_uhf)

if __name__ == "__main__":
    main()
