import os
import json
os.system('cls')
from .semiauto_ps import PSSE_ENGINE
from .semiauto_misc import exclude_connecting_bus,remove_internal_psse_buses,renumber_buses,write_status_report,find_buses,organize_connections,enforce_topological_order,solve_the_network, copy_and_rename
from .semiauto_rc import ReadConfigFile
import requests
import sys
from importlib.resources import files
from collections import OrderedDict


def send_request(api_url, key, email, app_id):
    try:
        response = requests.get(api_url, params={"key": key, "email": email, "app_id": app_id})
        if response.status_code == 200:
            print("Authentication Successful!")
        elif response.status_code == 403:
            print("Validation failed!")
        else:
            print(f"Unexpected response: {response.status_code}")
        return response
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def validate_key_and_email(key, email, app_id):
    api_urls = [
        "https://rkx6wbss34.execute-api.ap-southeast-2.amazonaws.com/default/ValidateKeyFunction",  # Sydney
        "https://keyactivation.onrender.com/validate-key/"
    ]
    
    for api_url in api_urls:
        response = send_request(api_url, key, email, app_id)
        if response:  # Exit on success (first successful request)
            return response
    
    return None  # Return None if no valid response is received from both APIs


##########for psse#############

def run_integration(file_path, file_name, user_email, user_key):

    def show_eula_and_get_consent():
        eula_path = files('snapshot_integration_package').joinpath('EULA')
        with eula_path.open('r', encoding='utf-8') as f:
            eula_text = f.read()
        print(eula_text)
        consent = input("Accept EULA (yes/no): ").strip().lower()
        if consent != 'yes':
            print("EULA not accepted. Exiting.")
            exit(1)

    # def get_eula_acceptance_path():
    #     # Store acceptance in a user-writeable config directory
    #     config_dir = os.path.join(os.path.expanduser("~"), ".snapshot_integration")
    #     os.makedirs(config_dir, exist_ok=True)
    #     return os.path.join(config_dir, "eula_accepted.json")
    
    def get_eula_acceptance_path():
        version_id = f"{sys.version_info.major}_{sys.version_info.minor}_{sys.version_info.micro}"
        config_dir = os.path.join(os.path.expanduser("~"), ".snapshot_integration")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, f"eula_accepted_py{version_id}.json")

    def has_accepted_eula():
        return os.path.exists(get_eula_acceptance_path())

    def store_acceptance():
        path = get_eula_acceptance_path()
        with open(path, "w") as f:
            json.dump({"accepted": True}, f)

    def enforce_eula():
        if not has_accepted_eula():
            show_eula_and_get_consent()
            store_acceptance()

    enforce_eula()

    app_id='app_snapshot_integration'

    response = validate_key_and_email(user_key, user_email, app_id)

    if response and response.status_code == 200:

        data = response.json()  # Parse the JSON response

        status = data.get('data', {}).get('status')  # Safely access 'status'

        if status == 'active':

            readfile = ReadConfigFile(file_path,file_name)

            softdata = readfile.get_soft_config_indexed_dict()
            maindata = readfile.get_main_config_indexed_dict()
            casedata = readfile.get_case_config_indexed_dict()

            for key, value in softdata.items():
                if value['attribute description'] == 'psse_path':
                    psse_path = value['attribute value']
                elif value['attribute description'] == 'psse_version':
                    version = value['attribute value']
                elif value['attribute description'] == 'psse_init':
                    nbus = value['attribute value']

            main_case_dict = OrderedDict()
            main_index = 0
            for key, value in maindata.items():
                if value['enabled'] in ['yes', 1, 1.0]:
                    main_case_dict[str(main_index)] = {
                        'filepath': value['snapshot filepath'],
                        'filename': value['snapshot filename']
                    }
                    main_index += 1

            small_case_dict = OrderedDict()
            small_index = 0
            for key, value in casedata.items():
                if value['enabled'] in ['yes', 1, 1.0]:
                    small_case_dict[str(small_index)] = {
                        'filepath': value['filepath of case to be added'],
                        'filename': value['name of case to be added'],
                        'connecting_bus': value['connecting bus number'],
                        'parent_path': value['parent_path']
                    }
                    small_index += 1

            psseng = PSSE_ENGINE(psse_path=psse_path,version=version)
            
            temp_files = list()
            
            try:

                for key in main_case_dict:
                    psse_initialized = False
                    main_case_name = main_case_dict[key]['filename'].split('.sav')[0]
                    main_case_path = main_case_dict[key]['filepath']
                    main_case_path = os.path.join(main_case_path, main_case_name + '.sav')
                    temp_mc_filepath = copy_and_rename(main_case_path)
                    temp_files.append(temp_mc_filepath)
                    # mc = psseng.get_case_data(main_case_path)
                    # mcbus = mc.pssbus
                    
                    sc_gen_dict = OrderedDict()
                    last_sc_accessed = None
                    
                    last_case = False
                    last_solve_success_case = None
                    directory_list = list()
                    directory_list_0 = list()
                    directory_list_renum = list()
                    
                    last_key = next(reversed(small_case_dict))

                    for jjj, key in enumerate(small_case_dict):
                        mc = psseng.get_case_data(temp_mc_filepath)
                        mcbus = mc.pssbus
                        last_sc_accessed = key
                        small_case_name = small_case_dict[key]['filename'].split('.sav')[0]
                        print('***********************************************************')
                        msg = f"Processing {main_case_name} with {small_case_name}"
                        print(msg)
                        small_case_path = small_case_dict[key]['filepath']
                        small_case_path = os.path.join(small_case_path, small_case_name + '.sav')
                        small_case = psseng.get_case_data(small_case_path)

                        connecting_bus = small_case_dict[key]['connecting_bus']
                        small_case.pssbus = exclude_connecting_bus(small_case,small_case.pssbus,connecting_bus)
                        small_case.pssbus = remove_internal_psse_buses(small_case.pssbus,small_case.pssbus)
                        small_case, renumber_map = renumber_buses(small_case,small_case.pssbus,mcbus,connecting_bus)

                        directory_to_save_files = os.path.join(small_case_dict[key]['parent_path'],small_case_name,main_case_name)
                        os.makedirs(directory_to_save_files, exist_ok=True)
                        
                        if connecting_bus not in mcbus['NUM']:
                            connecting_bus_not_found_file = os.path.join(directory_to_save_files, f"{main_case_name}_connecting_bus_not_found.txt")
                            with open(connecting_bus_not_found_file, 'w') as f:
                                    f.write(f"{connecting_bus} for {small_case_name} not found in {main_case_name}. LF solution not attempted. Please solve {small_case_name} manually or define connecting bus {connecting_bus} in {main_case_name} and re-run automation.\n")
                            
                            if small_case_dict[key]['parent_path'] not in directory_list_0:
                                directory_list_0.append(small_case_dict[key]['parent_path'])
                                new_directory_0 = True
                            else:
                                new_directory_0 = False
                                        
                            connecting_bus_not_found_file_2 = os.path.join(small_case_dict[key]['parent_path'], f"{main_case_name}_connecting_bus_not_found.txt")
                            if new_directory_0:
                                mode = 'w'
                            else:
                                mode = 'a'
                            with open(connecting_bus_not_found_file_2, mode) as f:
                                f.write(f"{connecting_bus} for {small_case_name} not found in {main_case_name}. LF solution not attempted. please solve manually or define connecting bus in {main_case_name} and re-run automation.\n")
                            
                        renumber_file = os.path.join(directory_to_save_files, f"{main_case_name}_renumber_map.txt")
                        with open(renumber_file, 'w') as f:
                            for old, new in renumber_map.items():
                                f.write(f"{old} -> {new}\n")
                                
                        renumber_file = os.path.join(directory_to_save_files, f"{main_case_name}_renumber_map.json")
                        with open(renumber_file, 'w') as f:
                            json.dump(renumber_map, f, indent=4)
                            
                        if small_case_dict[key]['parent_path'] not in directory_list_renum:
                            directory_list_renum.append(small_case_dict[key]['parent_path'])
                            new_directory_renum = True
                        else:
                            new_directory_renum = False
                                
                        renum_file2 = os.path.join(small_case_dict[key]['parent_path'], f"{main_case_name}_renumbered_bus.txt")
                        if new_directory_renum:
                            mode = 'w'
                        else:
                            mode = 'a'
                        with open(renum_file2, mode) as f:
                            f.write(f"Renumbered Buses in {small_case_name}\n")
                            for old, new in renumber_map.items():
                                f.write(f"{old} -> {new}\n")

                        
                        if jjj == 0:
                            ierr_init = psseng.init_psse(**{'buses': int(nbus)})
                            psse_initialized = True
                            main_case = psseng.open_case(**{'sfile' : main_case_path})

                        if psse_initialized:
                            progress_file = os.path.join(directory_to_save_files, f"progress.txt")
                            psseng.create_progress_output(**{'islct' : 2, 'filarg' : progress_file})

                            bus_status = psseng.add_buses(small_case,main_case_name,small_case_name,directory_to_save_files)
                            line_branch_status = psseng.add_line_branch(small_case,main_case_name,small_case_name,directory_to_save_files)
                            trn_branch_status = psseng.add_trn_branch(small_case,main_case_name,small_case_name,directory_to_save_files)
                            gen_status = psseng.add_gen(small_case,main_case_name,small_case_name,directory_to_save_files)
                            fsh_status = psseng.add_fixed_shunt(small_case,main_case_name,small_case_name,directory_to_save_files)
                            swsh_status = psseng.add_switched_shunt(small_case,main_case_name,small_case_name,directory_to_save_files)
                            add_load_status = psseng.add_load(small_case,main_case_name,small_case_name,directory_to_save_files)
                            ind_status = psseng.add_induction_machine(small_case,main_case_name,small_case_name,directory_to_save_files)
                            
                            psseng.save_case(**{'sfile' : temp_mc_filepath})
                            
                            sc_gen_dict[small_case_name] = small_case

                            added_small_case = os.path.join(directory_to_save_files, f"{main_case_name}_added_{small_case_name}")
                            psseng.save_case(**{'sfile' : added_small_case})

                            status_file = os.path.join(directory_to_save_files, f"{main_case_name}_status_{small_case_name}.txt")
                            
                            write_status_report(
                                                status_file,
                                                Bus_Status=bus_status,
                                                Line_Branch_Status=line_branch_status,
                                                Transformer_Branch_Status=trn_branch_status,
                                                Generator_Status=gen_status,
                                                Fixed_Shunt_Status=fsh_status,
                                                Switched_Shunt_Status=swsh_status,
                                                Load_Status=add_load_status,
                                                Induction_Machine_Status=ind_status
                                            )
                            
                            # # psseng.close_power_flow()
                            # # psseng.del_tmp_files()
                            # # psseng.open_case(**{'sfile' : added_small_case})

                            scbus_numbers =  [connecting_bus]  + list(small_case.pssbus['NUM'])

                            jkckt_list, jklckt_list = find_buses(scbus_numbers,psseng)
                            all_connections = organize_connections(connecting_bus, jkckt_list, jklckt_list)

                            ordered = enforce_topological_order(all_connections, connecting_bus)
                            # print(ordered)
                            
                            psseng.disconnect_buses(list(small_case.pssbus['NUM']))

                            save_outserv = os.path.join(directory_to_save_files, f"{main_case_name}_oos_{small_case_name.split('.sav')[0]}.sav")
                            psseng.save_case(**{'sfile' : save_outserv})

                            psseng.run_load_flow_rsol(options1=1, options2=2, options7=0, options9=1, options10=1)
                            ival_init = psseng.check_solved()
                            
                            if ival_init:
                                psseng.run_load_flow_rsol(options1=1, options2=2, options7=1, options9=1, options10=0)
                            ival_init = psseng.check_solved()
                            
                            if ival_init:
                                psseng.run_load_flow_rsol(options1=1, options2=2, options7=4, options9=1, options10=1)
                            ival_init = psseng.check_solved()
                            # ival_init = 0

                            save_solved = os.path.join(directory_to_save_files, f"{main_case_name}_solved_{small_case_name.split('.sav')[0]}_0.sav")
                            psseng.save_case(**{'sfile' : save_solved})

                            if not ival_init:
                                sav_file_name = os.path.join(directory_to_save_files, f"{main_case_name}_solved_{small_case_name.split('.sav')[0]}")
                                ival_lf, sav_case_returned, indx_returned = solve_the_network(psseng,sav_file_name,ordered)

                                if ival_lf:
                                    psseng.open_case(**{'sfile' : sav_case_returned})
                                    last_solve_success_case = sav_case_returned
                                    
                                    unsolved_file1 = os.path.join(directory_to_save_files, f"{main_case_name}_unsolved_lf.txt")
                                    with open(unsolved_file1, 'w') as f:
                                        f.write(f"unsolved generating system: {small_case_name} -> last_solve_success:{last_solve_success_case}\n")
                                    
                                    if small_case_dict[key]['parent_path'] not in directory_list:
                                        directory_list.append(small_case_dict[key]['parent_path'])
                                        new_directory = True
                                    else:
                                        new_directory = False
                                        
                                    unsolved_file2 = os.path.join(small_case_dict[key]['parent_path'], f"{main_case_name}_unsolved_lf.txt")
                                    if new_directory:
                                        mode = 'w'
                                    else:
                                        mode = 'a'
                                    with open(unsolved_file2, mode) as f:
                                        f.write(f"unsolved generating system: {small_case_name} -> last_solve_success:{last_solve_success_case}\n")
                                                
                                if not ival_lf and jjj == (len(small_case_dict) - 1):
                                    last_case = True
                                    psseng.save_case(**{'sfile' : os.path.join(small_case_dict[key]['parent_path'], main_case_name + '_solved' + '.sav')})
                                    psseng.close_power_flow()
                                    psseng.del_tmp_files()
                                    psseng.create_progress_output(**{'islct' : 6})
                                else:
                                    psseng.create_progress_output(**{'islct' : 6})
                            
                            else:
                                unsolved_file = os.path.join(directory_to_save_files, f"{main_case_name}_unsolved_lf.txt")
                                with open(unsolved_file, 'w') as f:
                                    f.write(f"unsolved: {small_case_name} -> last_solve_success:none, also check if the original {main_case_name} was solved.\n")
                        
                                if small_case_dict[key]['parent_path'] not in directory_list:
                                    directory_list.append(small_case_dict[key]['parent_path'])
                                    new_directory = True
                                else:
                                    new_directory = False
                                    
                                unsolved_file2 = os.path.join(small_case_dict[key]['parent_path'], f"{main_case_name}_unsolved_lf.txt")
                                if new_directory:
                                    mode = 'w'
                                else:
                                    mode = 'a'
                                with open(unsolved_file2, mode) as f:
                                    f.write(f"unsolved: {small_case_name} -> last_solve_success:none, also check if the original {main_case_name} was solved.\n")

                    if last_case:
                        psseng.open_case(**{'sfile' : os.path.join(small_case_dict[last_sc_accessed]['parent_path'], main_case_name + '_solved' + '.sav')})
                        for sc_name in sc_gen_dict:
                            psseng.modify_gen(sc_gen_dict[sc_name])
                        psseng.save_case(**{'sfile' : os.path.join(small_case_dict[last_sc_accessed]['parent_path'], main_case_name + '_solved' + '.sav')})
                    
                    gen_data_dict = OrderedDict()
                    for sc_name in sc_gen_dict:
                        gen_data_dict[sc_name] = psseng.get_gen_dict(sc_gen_dict[sc_name])
                    
                    gen_data_path = os.path.join(small_case_dict[last_key]['parent_path'], main_case_name + '_gen_data' + '.json')
                    with open(gen_data_path, 'w') as f:
                        json.dump(gen_data_dict, f, indent=4)
                    
                    # gen_data_path = os.path.join(small_case_dict[last_key]['parent_path'], main_case_name + '_gen_data' + '.txt')
                    # with open(gen_data_path, 'w') as f:
                    #     for key, value in gen_data_dict.items():
                    #         f.write(f'{key}: {value}\n')
            
            finally:
                temp_files = list(set(temp_files))
                [os.remove(file) for file in temp_files]
        
        else:
            print("key is not active!")
            
    else:
        print("Authentication Failed!")
