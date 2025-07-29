import numpy as np
from collections import deque
import shutil
import os


# Function to recursively convert NumPy types to normal Python types
def convert_np_types(data):
    if isinstance(data, dict):  # If the data is a dictionary
        return {key: convert_np_types(value) for key, value in data.items()}
    elif isinstance(data, tuple):  # If the data is a tuple
        return tuple(convert_np_types(value) for value in data)
    elif isinstance(data, list):  # If the data is a list
        return [convert_np_types(value) for value in data]
    elif isinstance(data, np.ndarray):  # If the data is a numpy array
        return data.tolist()  # Convert numpy array to a list
    elif isinstance(data, np.generic):  # If the data is a numpy scalar (e.g., np.int64, np.float64)
        return data.item()  # Convert numpy scalar to native Python type
    else:
        return data  # Return other data types as is


def renumber_value(bus_renumber_map,val):
    if isinstance(val, list):
        if all(isinstance(sub, list) for sub in val):  # list of lists
            return [[bus_renumber_map.get(item, item) for item in sublist] for sublist in val]
        else:  # flat list
            return [bus_renumber_map.get(item, item) for item in val]
    elif isinstance(val, tuple):
        return tuple(bus_renumber_map.get(item, item) for item in val)
    elif isinstance(val, np.ndarray):
        return np.vectorize(lambda x: bus_renumber_map.get(x, x))(val)
    else:
        return bus_renumber_map.get(val, val)


def renumber_field(bus_renumber_map,small_case, section, field):
    if hasattr(small_case, section):
        section_data = getattr(small_case, section)

        if isinstance(section_data, dict) and field in section_data:
            updated_section = section_data.copy()
            value = section_data[field]
            updated_section[field] = renumber_value(bus_renumber_map,value)
            setattr(small_case, section, updated_section)
            
    return small_case
 

def organize_connections(main_bus, branches, tx3s):
    graph = {}
    edge_map = {}

    seen_branch_keys = set()
    seen_tx3_keys = set()

    # --- 2-winding branch connections (deduplicate by unordered pair + ckt) ---
    for b1, b2, ckt in branches:
        key = (frozenset([b1, b2]), ckt.strip())
        if key in seen_branch_keys:
            continue
        seen_branch_keys.add(key)

        # Add to graph
        graph.setdefault(b1, []).append((b2, ckt, "branch"))
        graph.setdefault(b2, []).append((b1, ckt, "branch"))
        edge_map[key] = (b1, b2, ckt)

    # --- 3-winding transformers (deduplicate by unordered 3-bus set + ckt) ---
    for b1, b2, b3, ckt in tx3s:
        buses = [b for b in [b1, b2, b3] if b != 0]
        key = (frozenset(buses), ckt.strip())
        if key in seen_tx3_keys:
            continue
        seen_tx3_keys.add(key)

        # Add all bus pairs to graph
        for i in range(len(buses)):
            for j in range(i + 1, len(buses)):
                bus_i, bus_j = buses[i], buses[j]
                pair_key = (frozenset([bus_i, bus_j]), ckt.strip())
                graph.setdefault(bus_i, []).append((bus_j, ckt, "tx3"))
                graph.setdefault(bus_j, []).append((bus_i, ckt, "tx3"))
                edge_map[pair_key] = (b1, b2, b3, ckt)

    # --- BFS traversal ---
    visited_buses = set()
    visited_edges = set()
    queue = deque([main_bus])
    ordered = []

    while queue:
        bus = queue.popleft()
        if bus in visited_buses:
            continue
        visited_buses.add(bus)

        for nbr, ckt, etype in graph.get(bus, []):
            edge_key = (frozenset([bus, nbr]), ckt.strip())
            if edge_key in visited_edges:
                continue
            visited_edges.add(edge_key)

            conn = edge_map[edge_key]
            if conn not in ordered:
                ordered.append(conn)
            if nbr not in visited_buses:
                queue.append(nbr)

    return ordered



def find_buses(scbus_numbers,psseng):
    jkckt_list = []
    jklckt_list = []
    for bus in scbus_numbers:
        # print("Visiting:", connecting_bus)
        # --- 2-winding branches ---
        ierr, isect = psseng.ini_branch_2(**{'ibus': bus, 'inode'  : 0, 'single' : 2})
        while True:
            ierr1, jbus1, jsect1, ckt1 = psseng.get_next_branch_bus(**{'ibus': bus, 'inode' : 0})
            if ierr1 != 0:
                break
            else:
                if jbus1 in scbus_numbers:
                    jkckt_list.append((bus,jbus1,ckt1))

        # --- 3-winding transformers ---
        ierr, isect = psseng.ini_branch_2(**{'ibus': bus, 'inode'  : 0, 'single' : 2})
        while True:
            ierr2, jbus2, jsect2, kbus2, ksect2, ckt2 = psseng.get_next_tx3_bus(**{'ibus': bus, 'inode' : 0})
            if ierr2 != 0:
                break
            else:
                if (jbus2 in scbus_numbers or jbus2 in [0]) and (kbus2 in scbus_numbers or kbus2 in [0]):
                    jklckt_list.append((bus,jbus2,kbus2,ckt2))

    return jkckt_list, jklckt_list


def validate_bus_renumbering(small_case,bus_renumber_map):
    all_updated = True

    for section, field in [
        ('pssbus', 'NUM'),
        ('psslod', 'NUM'),
        ('pssfsh', 'NUM'),
        ('pssgen', 'NUM'),('pssgen', 'IREG'),
        ('psswsh', 'NUM'),('psswsh', 'SWREM'),
        ('psssub', 'NUM'),
        ('pssind', 'NUM'),
        ('pssald', 'NUM'),
        ('psstrn', 'CONBUS'),
        ('pssabx', 'FRMBUS'), ('pssabx', 'TOBUS'),
        ('pssmsl', 'FRMBUS'), ('pssmsl', 'TOBUS'), ('pssmsl', 'DUMBUS'), ('pssmsl', 'METBUS'),
        ('pssbrn', 'FRMBUS'), ('pssbrn', 'TOBUS'), ('pssbrn', 'METBUS'),
        ('pss3wt', 'BUS1ST'), ('pss3wt', 'BUS2ND'), ('pss3wt', 'BUS3RD'), ('pss3wt', 'NMETER'),
        ('casbrn', 'FRMBUS'), ('casbrn', 'TOBUS'), ('casbrn', 'METBUS'),
        ('castrn', 'BUSNUM'), ('castrn', 'METBUS'), ('castrn', 'CONBUS')
    ]:
        section_data = getattr(small_case, section, {})
        if not section_data or field not in section_data:
            print(f"Field '{field}' not found in section '{section}'.")
            all_updated = False
            continue

        field_data = section_data[field]

        def check_and_report(val, path=''):
            nonlocal all_updated
            if isinstance(val, list):
                if all(isinstance(x, list) for x in val):  # list of lists
                    for i, sub in enumerate(val):
                        check_and_report(sub, f"{path}[{i}]")
                else:
                    for i, x in enumerate(val):
                        original = [k for k, v in bus_renumber_map.items() if v == x]
                        if original and x != bus_renumber_map.get(original[0], x):
                            print(f"Mismatch at {section}->{field}{path}[{i}]: expected {bus_renumber_map.get(original[0])}, got {x}")
                            all_updated = False
            elif isinstance(val, tuple):
                for i, x in enumerate(val):
                    original = [k for k, v in bus_renumber_map.items() if v == x]
                    if original and x != bus_renumber_map.get(original[0], x):
                        print(f"Mismatch at {section}->{field}{path}({i}): expected {bus_renumber_map.get(original[0])}, got {x}")
                        all_updated = False
            elif isinstance(val, np.ndarray):
                for i, x in np.ndenumerate(val):
                    original = [k for k, v in bus_renumber_map.items() if v == x]
                    if original and x != bus_renumber_map.get(original[0], x):
                        print(f"Mismatch at {section}->{field}{path}{i}: expected {bus_renumber_map.get(original[0])}, got {x}")
                        all_updated = False
            else:
                original = [k for k, v in bus_renumber_map.items() if v == val]
                if original and val != bus_renumber_map.get(original[0], val):
                    print(f"ismatch at {section}->{field}{path}: expected {bus_renumber_map.get(original[0])}, got {val}")
                    all_updated = False

        check_and_report(field_data)

    return all_updated

def reorder_edge(edge, root):
    *buses, ckt = edge
    nonzero_buses = [b for b in buses if b != 0]
    if root in nonzero_buses:
        return tuple([root] + [b for b in nonzero_buses if b != root] + [ckt])
    else:
        return tuple(nonzero_buses + [ckt])
    
# Step 2: Reorder buses in topological direction from main bus
def enforce_topological_order(connections, main_bus):

    # Build adjacency map
    graph = {}
    for conn in connections:
        *buses, ckt = conn
        buses = [b for b in buses if b != 0]
        for b in buses:
            graph.setdefault(b, set()).update(set(buses) - {b})

    # BFS to record visitation order
    visited = {}
    queue = deque([main_bus])
    step = 0

    while queue:
        bus = queue.popleft()
        if bus in visited:
            continue
        visited[bus] = step
        step += 1
        for nbr in graph.get(bus, []):
            if nbr not in visited:
                queue.append(nbr)

    # Reorder each connection based on visited order
    ordered = []
    for conn in connections:
        *buses, ckt = conn
        buses = [b for b in buses if b != 0]
        buses.sort(key=lambda x: visited.get(x, float('inf')))
        ordered.append(tuple(buses + [ckt]))

    return ordered


def exclude_connecting_bus(small_case,scbus,connecting_bus):
    # Check if connecting_bus exists in 'NUM'
    if connecting_bus is not None and connecting_bus in scbus['NUM']:
        # Find index of the bus to remove
        index_to_remove = scbus['NUM'].index(connecting_bus)
    
        # Create a new dict with filtered entries (excluding the index_to_remove)
        scbus = {
            key: tuple(val[i] for i in range(len(val)) if i != index_to_remove)
            for key, val in scbus.items() if isinstance(val, tuple)
        }
    
        # If 'IERR' exists and is not a tuple, keep it as-is
        if 'IERR' in small_case.pssbus:
            scbus['IERR'] = small_case.pssbus['IERR']
    return scbus


def remove_internal_psse_buses(pssbus,scbus):
    # Step 1: Extract bus numbers from 'NUM'
    bus_nums = np.array(pssbus['NUM'])

    # Step 2: Create a mask for bus numbers with ≤ 6 digits
    mask = bus_nums <= 999999

    # Step 3: Apply mask to all entries (except scalar ones like 'IERR')
    pssbus_filtered = {}
    for key, values in pssbus.items():
        if isinstance(values, tuple) and len(values) == len(bus_nums):
            pssbus_filtered[key] = tuple(np.array(values)[mask])
        else:
            # Copy scalar values like 'IERR' without modification
            pssbus_filtered[key] = values
    
    scbus.update(convert_np_types(pssbus_filtered))

    return scbus


def renumber_buses(small_case,scbus,mcbus,connecting_bus):
        # Identify conflicts
        # Renumber only if conflicts exist
        
        main_bus_nums = set(mcbus['NUM'])
        small_bus_nums = np.array(scbus['NUM'])
        conflicting = np.isin(small_bus_nums, list(main_bus_nums))
        bus_renumber_map = {}

        new_nums = small_bus_nums.copy()
        candidate = 900000  # Start renumbering from this base

        for i, old_num in enumerate(small_bus_nums):
            if old_num not in [connecting_bus]:
                if old_num in main_bus_nums:
                    while candidate in main_bus_nums or candidate in bus_renumber_map.values():
                        candidate += 1
                        if candidate > 999999:
                            candidate = 900000  # Wrap around
                    new_num = candidate
                    bus_renumber_map[old_num] = new_num
                    new_nums[i] = new_num

        # Convert keys and values to native Python int
        renumber_map = {int(k): int(v) for k, v in bus_renumber_map.items()}

        # Now apply renumbering only if the map has entries
        if bus_renumber_map:
            print("Conflicting bus numbers found. Renumbering...")
            for section, field in [
                ('pssbus', 'NUM'),
                ('psslod', 'NUM'),
                ('pssfsh', 'NUM'),
                ('pssgen', 'NUM'),('pssgen', 'IREG'),
                ('psswsh', 'NUM'),('psswsh', 'SWREM'),
                ('psssub', 'NUM'),
                ('pssind', 'NUM'),
                ('pssald', 'NUM'),
                ('psstrn', 'CONBUS'),
                ('pssabx', 'FRMBUS'), ('pssabx', 'TOBUS'),
                ('pssmsl', 'FRMBUS'), ('pssmsl', 'TOBUS'), ('pssmsl', 'DUMBUS'), ('pssmsl', 'METBUS'),
                ('pssbrn', 'FRMBUS'), ('pssbrn', 'TOBUS'), ('pssbrn', 'METBUS'),
                ('pss3wt', 'BUS1ST'), ('pss3wt', 'BUS2ND'), ('pss3wt', 'BUS3RD'), ('pss3wt', 'NMETER'),
                ('casbrn', 'FRMBUS'), ('casbrn', 'TOBUS'), ('casbrn', 'METBUS'),
                ('castrn', 'BUSNUM'), ('castrn', 'METBUS'), ('castrn', 'CONBUS')
            ]:
                _small_case_ = renumber_field(bus_renumber_map,small_case, section, field)
            
            # Run the validation
            if validate_bus_renumbering(small_case, bus_renumber_map):
                print("Bus numbers have been successfully renumbered.")
            else:
                print("Some bus numbers may not have been renumbered correctly.")

        else:
            _small_case_ = small_case
            print("No conflicting buses found. No renumbering needed.")
        
        return _small_case_, renumber_map



def write_status_report(filename, **statuses):
    def format_dict(d, indent=0):
        lines = []
        for key, value in d.items():
            if isinstance(value, dict):
                lines.append(" " * indent + f"{key}:")
                lines.extend(format_dict(value, indent + 4))
            else:
                lines.append(" " * indent + f"{key}: {value}")
        return lines

    with open(filename, 'w') as f:
        for category, status_dict in statuses.items():
            f.write(f"{category}:\n")
            formatted = format_dict(status_dict, indent=4)
            f.write("\n".join(formatted))
            f.write("\n\n")  # Separate sections



def solve_the_network(psseng,sav_file_name,ordered):
        
    ival_lf = 0
    indx = 0
    
    sav_case_to_return = None
    
    seen_links = set()  # To track what’s already reconnected
    
    for bs in ordered:
        if not ival_lf:
            print(f"Reconnecting buses: {bs}")
            condition = False  # General flag for reconnection
            if len(bs) == 3:
                # 2-winding or partial TX3
                key = tuple(sorted([bs[0], bs[1]]) + [bs[2].strip()])
                if key not in seen_links:
                    condition = True
                    seen_links.add(key)
    
            elif len(bs) == 4:
                # Full 3-winding transformer
                buses = [bs[0], bs[1], bs[2]]
                key = tuple(sorted(buses) + [bs[3].strip()])
                if key not in seen_links:
                    condition = True
                    seen_links.add(key)    
    
            if condition:
                ierr, rval1 = psseng.get_bus_data(ibus=bs[0], string='PU')
                ierr, rval2 = psseng.get_bus_data(ibus=bs[0], string='ANGLED')
    
                # reconnect and set voltage for all involved buses
                # for b in bs[1:-1]:  # skip last item (ckt ID)
                for b in bs[1:len(bs)-1]:  # skip last item (ckt ID)
                    psseng.reconnect_buses(b)
                    ierr = psseng.ini_mac(**{'ibus' :b})
                    ierr11 = 0
                    while not ierr11:
                        ierr11, id = psseng.next_mac(**{'ibus': b})
                        if not ierr11:
                            ierr = psseng.change_machine_data(**{'ibus':b, 'id':id, 'intgar1':0})
                    ierr = psseng.change_bus_data(**{'ibus':b, 'inode':0, 'realar2':rval1, 'realar3':rval2})
                
                ierr_lf = psseng.run_load_flow_rsol(**{'options1': 1, 'options2': 2, 'options6': 1, 'options7': 0, 'options8': 99, 'options9': 0, 'options10': 0})
                ival_lf = psseng.check_solved()
                
                if ival_lf:
                    ierr_lf = psseng.run_load_flow_rsol(**{'options1': 1, 'options2': 2, 'options6': 1, 'options7': 1, 'options8': 99, 'options9': 0, 'options10': 0})
                    ierr_lf = psseng.run_load_flow_rsol(**{'options1': 1, 'options2': 2, 'options6': 1, 'options7': 1, 'options8': 99, 'options9': 0, 'options10': 0})
                    ival_lf = psseng.check_solved()
                    if not ival_lf:
                        psseng.run_load_flow_fnsl(**{'options1': 2, 'options4': 1, 'options5': 1, 'options6': 0, 'options7': 99, 'options8': 0})
                        ival_lf = psseng.check_solved()
                    
                if not ival_lf:
                    ierr_lf = psseng.run_load_flow_rsol(**{'options1': 1, 'options2': 2, 'options6': 1, 'options7': 0, 'options8': 99, 'options9': 0, 'options10': 0})
                    ival_lf = psseng.check_solved()
                    psseng.run_load_flow()
                
                psseng.run_load_flow_fnsl(**{'options1': 2, 'options4': 1, 'options5': 1, 'options6': 0, 'options7': 99, 'options8': 0})
                ival_lf = psseng.check_solved()
                kkkk = 0
                while ival_lf and kkkk <= 5:
                    psseng.run_load_flow()
                    psseng.run_load_flow_fnsl(**{'options1': 2, 'options4': 1, 'options5': 1, 'options6': 0, 'options7': 99, 'options8': 0})
                    ival_lf = psseng.check_solved()
                    kkkk += 1

                ierr_lf = psseng.run_load_flow_rsol(**{'options1': 1, 'options2': 2, 'options6': 1, 'options7': 0, 'options8': 99, 'options9': 0, 'options10': 0})
                ival_lf = psseng.check_solved()
                if ival_lf:
                    ierr_lf = psseng.run_load_flow_rsol(**{'options1': 1, 'options2': 2, 'options6': 1, 'options7': 1, 'options8': 99, 'options9': 0, 'options10': 1})
                ival_lf = psseng.check_solved()
                if ival_lf:
                    ierr_lf = psseng.run_load_flow_rsol(**{'options1': 1, 'options2': 2, 'options6': 1, 'options7': 2, 'options8': 99, 'options9': 0, 'options10': 1})
                ival_lf = psseng.check_solved()
                if ival_lf:
                    ierr_lf = psseng.run_load_flow_rsol(**{'options1': 1, 'options2': 2, 'options6': 1, 'options7': 4, 'options8': 99, 'options9': 0, 'options10': 1})
                ival_lf = psseng.check_solved()
                if ival_lf:
                    ierr_lf = psseng.run_load_flow_rsol(**{'options1': 1, 'options2': 2, 'options6': 1, 'options7': 0, 'options8': 99, 'options9': 0, 'options10': 1})
                ierr_lf = psseng.run_load_flow_fnsl(**{'options1': 2, 'options4': 1, 'options5': 1, 'options6': 0, 'options7': 99, 'options8': 0})
                ival_lf = psseng.check_solved()
                if ival_lf:
                    ierr_lf = psseng.run_load_flow_fnsl(**{'options1': 2, 'options4': 1, 'options5': 1, 'options6': 0, 'options7': 99, 'options8': 0})
                
                ierr_lf = psseng.run_load_flow_fnsl(**{'options1': 2, 'options4': 1, 'options5': 1, 'options6': 0, 'options7': 99, 'options8': 0})
                ival_lf = psseng.check_solved()
                
                if not ival_lf:
                    psseng.save_case(**{'sfile' : f"{sav_file_name}_{indx+1}.sav"})
                    indx += 1
        else:
            sav_case_to_return = f"{sav_file_name}_{indx}.sav"
    
    if not ival_lf:
        psseng.save_case(**{'sfile' : f"{sav_file_name}_final_solved.sav"})
        # psspy.close_powerflow()
        # psspy.deltmpfiles()
    
    return ival_lf, sav_case_to_return, indx



def copy_and_rename(source_file):
    # Define the directory and the base name for the new file
    dir_path = os.path.dirname(source_file)
    base_name = os.path.basename(source_file)
    
    # Remove the file extension
    name, ext = os.path.splitext(base_name)
    
    # Set the new file name, starting with "_copy" as a base
    new_file = os.path.join(dir_path, f"{name}_copy{ext}")
    
    # Ensure the new file name is unique
    counter = 1
    while os.path.exists(new_file):
        new_file = os.path.join(dir_path, f"{name}_copy_{counter}{ext}")
        counter += 1
    
    # Copy the file to the new name
    shutil.copy(source_file, new_file)
    
    return new_file