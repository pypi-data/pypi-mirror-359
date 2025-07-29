import sys
import os
from collections import OrderedDict


class PSSE_ENGINE():
    def __init__(self, psse_path, version):
        self.psse_path = str(psse_path)
        self.version = float(version)
        self.caspy, self.psspy = self.get_modules()


    def get_modules(self):
        sys.path.append(self.psse_path)
        if self.version >= 36.2:
            import psse3602
            import caspy
            import psspy
            return caspy, psspy
        elif self.version >= 36.1:
            import psse3601
            import caspy
            import psspy
            return caspy, psspy
        elif self.version >= 35.5:
            import psse3505
            import caspy
            import psspy
            return caspy, psspy
        elif self.version >= 34.0:
            import psse34
            import caspy
            import psspy
            return caspy, psspy


    def create_progress_output(self,**kwargs):
        error = self.psspy.progress_output(**kwargs)
        if not error:
            self.psspy.lines_per_page_one_device(1,10000000)
            return 0


    def init_psse(self, **kwargs):
        return self.psspy.psseinit(**kwargs)


    def get_caspy(self):
        return self.caspy
    

    def get_psspy(self):
        return self.psspy


    def run_load_flow(self):
        self.psspy.rsol(options1=1, options2=2, options6=1, options7=0, options8=99, options9=0, options10=0)
        self.psspy.rsol([1,2,0,0,1,1,0,99,0,0],[500.0,5.0])
        self.psspy.rsol([1,2,0,0,1,1,0,99,0,0],[500.0,5.0])
        self.psspy.fnsl([2,0,0,1,1,0,99,0])
        self.psspy.fnsl([2,0,0,1,1,0,99,0])
        self.psspy.rsol([1,2,0,0,1,1,0,99,0,0],[500.0,5.0])
        self.psspy.fnsl([2,0,0,1,1,4,99,0])
        self.psspy.fnsl([2,0,0,1,1,4,99,0])
        self.psspy.rsol([1,2,0,0,1,1,4,99,0,0],[500.0,5.0])
        self.psspy.rsol([1,2,0,0,1,1,0,99,0,0],[500.0,5.0])


    def run_load_flow_rsol(self, **kwargs):
        self.psspy.rsol(**kwargs)


    def run_load_flow_fnsl(self, **kwargs):
        self.psspy.fnsl(**kwargs)


    def check_solved(self):
        return self.psspy.solved()
    

    def get_next_branch_bus(self, **kwargs):
        return self.psspy.nxtbrn_2(**kwargs)


    def get_next_tx3_bus(self, **kwargs):
        return self.psspy.nxtbrn3_2(**kwargs)


    def ini_branch_2(self, **kwargs):
        return self.psspy.inibrn_2(**kwargs)


    def ini_mac(self, **kwargs):
            return self.psspy.inimac(**kwargs)
    

    def next_mac(self, **kwargs):
            return self.psspy.nxtmac(**kwargs)
    

    def get_case_data(self, case):
        return self.caspy.Savecase(case)
    

    def disconnect_buses(self, bus_numbers):
        if isinstance(bus_numbers, list):
            for bus in bus_numbers:
                self.psspy.dscn(bus)
        else:
            self.psspy.dscn(bus_numbers)
        
        
    def reconnect_buses(self, bus_numbers):
        if isinstance(bus_numbers, list):
            for bus in bus_numbers:
                self.psspy.recn(bus)
        else:
            self.psspy.recn(bus_numbers)


    def save_case(self, **kwargs):
            return self.psspy.save(**kwargs)
    

    def close_power_flow(self):
            return self.psspy.close_powerflow()
    

    def del_tmp_files(self):
            return self.psspy.deltmpfiles()


    def open_case(self, **kwargs):
            return self.psspy.case(**kwargs)
    

    def get_bus_data(self, **kwargs):
            return self.psspy.busdat(**kwargs)

    def change_machine_data(self, **kwargs):
            if self.version >= 36.0:
                return self.psspy.machine_chng_5(**kwargs)
            elif self.version >= 35.5:
                return self.psspy.machine_chng_4(**kwargs)
            elif self.version >= 35.0:
                return self.psspy.machine_chng_3(**kwargs)
            elif self.version >= 33.0:
                return self.psspy.machine_chng_2(**kwargs)
    

    def change_bus_data(self, **kwargs):
            return self.psspy.bus_chng_4(**kwargs)


    def add_buses(self,small_case,main_case_name,small_case_name,directory_to_save_files):
        save_bus_name = f'{main_case_name}_added_bus_{small_case_name}'
        # self.open_case(**{'sfile' : case_to_use})
        bus_status = OrderedDict()
        sc_bus = small_case.pssbus
        total_bus = len(sc_bus['NUM'])
        bus_status.update(total_bus=total_bus)
        for i in range(total_bus):
            ierr = self.psspy.bus_data_4(ibus=sc_bus['NUM'][i], 
                                    inode=0, 
                                    intgar1=sc_bus['IDE'][i],
                                    intgar2=sc_bus['AREA'][i],
                                    intgar3=sc_bus['ZONE'][i],
                                    intgar4=sc_bus['OWNER'][i],
                                    realar1=sc_bus['BASKV'][i],
                                    realar2=sc_bus['VM'][i],
                                    realar3=sc_bus['VA'][i],
                                    realar4=sc_bus['NMAXV'][i],
                                    realar5=sc_bus['NMINV'][i],
                                    realar6=sc_bus['EMAXV'][i],
                                    realar7=sc_bus['EMINV'][i],
                                    name=sc_bus['NAME'][i]
                                    )
            
            bus_status.update({f"{sc_bus['NUM'][i]}":ierr})
        
        save_bus = os.path.join(directory_to_save_files, save_bus_name)
        self.psspy.save(save_bus)
        # self.psspy.close_powerflow()
        # self.psspy.deltmpfiles()

        return bus_status


    def add_line_branch(self,small_case,main_case_name,small_case_name,directory_to_save_files):
        save_line_branch_name = f'{main_case_name}_added_line_{small_case_name}'
        # self.open_case(**{'sfile' : case_to_use})
        line_branch_status = OrderedDict()
        sc_line_branch = small_case.casbrn
        total_line_branch = small_case.cas_nbrn
        line_branch_status.update(total_line_branch=total_line_branch)
        
        if self.version >= 36.0:
            _func_ = self.psspy.branch_data_4
        elif self.version >= 34.0:
            _func_ = self.psspy.branch_data_3
        
        for i in range(total_line_branch):
            ierr = _func_(ibus=sc_line_branch['FRMBUS'][i],
                                    jbus=sc_line_branch['TOBUS'][i],
                                    ckt=sc_line_branch['CKT'][i], 
                                    intgar1=sc_line_branch['STAT'][i],
                                    intgar2=sc_line_branch['METBUS'][i],
                                    intgar3=sc_line_branch['OWNER'][i][0],
                                    intgar4=sc_line_branch['OWNER'][i][1],
                                    intgar5=sc_line_branch['OWNER'][i][2],
                                    intgar6=sc_line_branch['OWNER'][i][3],
                                    #    intgar7=sc_line_branch['BYPASS'][i],
                                    realar1=sc_line_branch['RX'][i].real,
                                    realar2=sc_line_branch['RX'][i].imag,
                                    realar3=sc_line_branch['B'][i],
                                    realar4=sc_line_branch['GBI'][i].real,
                                    realar5=sc_line_branch['GBI'][i].imag,
                                    realar6=sc_line_branch['GBJ'][i].real,
                                    realar7=sc_line_branch['GBJ'][i].imag,
                                    realar8=sc_line_branch['LINLEN'][i],
                                    realar9 =sc_line_branch['OWNPCT'][i][0],
                                    realar10=sc_line_branch['OWNPCT'][i][1],
                                    realar11=sc_line_branch['OWNPCT'][i][2],
                                    realar12=sc_line_branch['OWNPCT'][i][3],
                                    ratings1=sc_line_branch['RATINGS'][i][0],
                                    ratings2=sc_line_branch['RATINGS'][i][1],
                                    ratings3=sc_line_branch['RATINGS'][i][2],
                                    ratings4=sc_line_branch['RATINGS'][i][3],
                                    ratings5=sc_line_branch['RATINGS'][i][4],
                                    ratings6=sc_line_branch['RATINGS'][i][5],
                                    ratings7=sc_line_branch['RATINGS'][i][6],
                                    ratings8=sc_line_branch['RATINGS'][i][7],
                                    ratings9=sc_line_branch['RATINGS'][i][8],
                                    ratings10=sc_line_branch['RATINGS'][i][9],
                                    ratings11=sc_line_branch['RATINGS'][i][10],
                                    ratings12=sc_line_branch['RATINGS'][i][11],
                                    namear=sc_line_branch['BRNAME'][i]
                                    )
            line_branch_status.update({f"{sc_line_branch['FRMBUS'][i]} to {sc_line_branch['TOBUS'][i]}, Ckt:{sc_line_branch['CKT'][i]}":ierr})
        
        save_line_branch = os.path.join(directory_to_save_files, save_line_branch_name)    
        self.psspy.save(save_line_branch)
        # self.psspy.close_powerflow()
        # self.psspy.deltmpfiles()
        
        return line_branch_status


    def add_trn_branch(self,small_case,main_case_name,small_case_name,directory_to_save_files):
        save_trn_branch_name = f'{main_case_name}_added_trn_{small_case_name}'
        # self.open_case(**{'sfile' : case_to_use})
        trn_branch_status = OrderedDict()
        sc_trn_branch = small_case.castrn
        total_trn_branch = small_case.cas_ntrn
        trn_branch_status.update(total_trn_branch=total_trn_branch)
        for i in range(total_trn_branch):
            if sc_trn_branch['BUSNUM'][i][2] == 0:
                ierr = self.psspy.two_winding_data_6(ibus=sc_trn_branch['BUSNUM'][i][0],
                                                jbus=sc_trn_branch['BUSNUM'][i][1],
                                                ckt=sc_trn_branch['CKT'][i], 
                                                intgar1=sc_trn_branch['STAT'][i],
                                                intgar2=sc_trn_branch['METBUS'][i],
                                                intgar3=sc_trn_branch['OWNER'][i][0],
                                                intgar4=sc_trn_branch['OWNER'][i][1],
                                                intgar5=sc_trn_branch['OWNER'][i][2],
                                                intgar6=sc_trn_branch['OWNER'][i][3],
                                                intgar7=sc_trn_branch['NTAPS'][i][0] if sc_trn_branch['NTAPS'][i][0] != 0 else sc_trn_branch['NTAPS'][i][1],
                                                intgar8=sc_trn_branch['TABLE'][i][0],
                                                # intgar9=sc_trn_branch['WN1BUS'][i],
                                                intgar10=sc_trn_branch['CONBUS'][i][0] if sc_trn_branch['CONBUS'][i][0] != 0 else sc_trn_branch['CONBUS'][i][1],
                                                intgar11=sc_trn_branch['NOD'][i][0] if self.version > 34 else 0,
                                                # intgar12=sc_branch['SICOD1'][i],
                                                intgar13=sc_trn_branch['CNTL'][i][0] if sc_trn_branch['CNTL'][i][0] != 0 else sc_trn_branch['CNTL'][i][1],
                                                intgar14=sc_trn_branch['CW'][i],
                                                intgar15=sc_trn_branch['CZ'][i],
                                                intgar16=sc_trn_branch['CM'][i],
                                                realari1=sc_trn_branch['RX'][i][0].real,
                                                realari2=sc_trn_branch['RX'][i][0].imag,
                                                realari3=sc_trn_branch['SBASE'][i][0],
                                                realari4=sc_trn_branch['WIND'][i][0],
                                                realari5=sc_trn_branch['NOMV'][i][0],
                                                realari6=sc_trn_branch['ANG'][i][0] if sc_trn_branch['ANG'][i][0] != 0 else sc_trn_branch['ANG'][i][1],
                                                realari7=sc_trn_branch['WIND'][i][1],
                                                realari8=sc_trn_branch['NOMV'][i][1],
                                                realari9 =sc_trn_branch['OWNPCT'][i][0],
                                                realari10=sc_trn_branch['OWNPCT'][i][1],
                                                realari11=sc_trn_branch['OWNPCT'][i][2],
                                                realari12=sc_trn_branch['OWNPCT'][i][3],
                                                realari13=sc_trn_branch['MAG1'][i],
                                                realari14=sc_trn_branch['MAG2'][i],
                                                realari15=sc_trn_branch['RMAX'][i][0] if sc_trn_branch['RMAX'][i][0] != 0 else sc_trn_branch['RMAX'][i][1],
                                                realari16=sc_trn_branch['RMIN'][i][0] if sc_trn_branch['RMIN'][i][0] != 0 else sc_trn_branch['RMIN'][i][1],
                                                realari17=sc_trn_branch['VMAX'][i][0] if sc_trn_branch['VMAX'][i][0] != 0 else sc_trn_branch['VMAX'][i][1],
                                                realari18=sc_trn_branch['VMIN'][i][0] if sc_trn_branch['VMIN'][i][0] != 0 else sc_trn_branch['VMIN'][i][1],
                                                realari19=sc_trn_branch['XFRCMP'][i][0].real,
                                                realari20=sc_trn_branch['XFRCMP'][i][0].imag,
                                                realari21=sc_trn_branch['CNXA'][i][0],
                                                ratings1=sc_trn_branch['RATINGS'][i][0][0],
                                                ratings2=sc_trn_branch['RATINGS'][i][0][1],
                                                ratings3=sc_trn_branch['RATINGS'][i][0][2],
                                                ratings4=sc_trn_branch['RATINGS'][i][0][3],
                                                ratings5=sc_trn_branch['RATINGS'][i][0][4],
                                                ratings6=sc_trn_branch['RATINGS'][i][0][5],
                                                ratings7=sc_trn_branch['RATINGS'][i][0][6],
                                                ratings8=sc_trn_branch['RATINGS'][i][0][7],
                                                ratings9=sc_trn_branch['RATINGS'][i][0][8],
                                                ratings10=sc_trn_branch['RATINGS'][i][0][9],
                                                ratings11=sc_trn_branch['RATINGS'][i][0][10],
                                                ratings12=sc_trn_branch['RATINGS'][i][0][11],
                                                namear=sc_trn_branch['TRNAME'][i],
                                                vgrpar=sc_trn_branch['VECGRP'][i]
                                                )
                trn_branch_status.update({f"{sc_trn_branch['BUSNUM'][i][0]} to {sc_trn_branch['BUSNUM'][i][1]}, Ckt:{sc_trn_branch['CKT'][i]}":ierr[0]})
            else:
                ierr = self.psspy.three_wnd_imped_data_4(ibus=sc_trn_branch['BUSNUM'][i][0],
                                                    jbus=sc_trn_branch['BUSNUM'][i][1],
                                                    kbus=sc_trn_branch['BUSNUM'][i][2],
                                                    ckt=sc_trn_branch['CKT'][i], 
                                                    intgar1=sc_trn_branch['OWNER'][i][0],
                                                    intgar2=sc_trn_branch['OWNER'][i][1],
                                                    intgar3=sc_trn_branch['OWNER'][i][2],
                                                    intgar4=sc_trn_branch['OWNER'][i][3],
                                                    intgar5=sc_trn_branch['CW'][i],
                                                    intgar6=sc_trn_branch['CZ'][i],
                                                    intgar7=sc_trn_branch['CM'][i],
                                                    intgar8=sc_trn_branch['STAT'][i],
                                                    intgar9=sc_trn_branch['METBUS'][i],
                                                    # intgar10=sc_trn_branch[''][i],
                                                    # intgar11=sc_trn_branch[''][i],
                                                    # intgar12=sc_trn_branch[''][i],
                                                    intgar12=sc_trn_branch['ZCOD'][i] if self.version > 34 else 0,
                                                    realari1=sc_trn_branch['RX'][i][0].real,
                                                    realari2=sc_trn_branch['RX'][i][0].imag,
                                                    realari3=sc_trn_branch['RX'][i][1].real,
                                                    realari4=sc_trn_branch['RX'][i][1].imag,
                                                    realari5=sc_trn_branch['RX'][i][2].real,
                                                    realari6=sc_trn_branch['RX'][i][2].imag,
                                                    realari7=sc_trn_branch['SBASE'][i][0],
                                                    realari8=sc_trn_branch['SBASE'][i][1],
                                                    realari9=sc_trn_branch['SBASE'][i][2],
                                                    realari10=sc_trn_branch['MAG1'][i],
                                                    realari11=sc_trn_branch['MAG2'][i],
                                                    realari12=sc_trn_branch['OWNPCT'][i][0],
                                                    realari13=sc_trn_branch['OWNPCT'][i][1],
                                                    realari14=sc_trn_branch['OWNPCT'][i][2],
                                                    realari15=sc_trn_branch['OWNPCT'][i][3],
                                                    # realari16=sc_trn_branch[''][][],
                                                    # realari17=sc_trn_branch[''][][],
                                                    namear=sc_trn_branch['TRNAME'][i],
                                                    vgrpar=sc_trn_branch['VECGRP'][i]
                                                    )
                trn_branch_status.update({f"{sc_trn_branch['BUSNUM'][i][0]} to {sc_trn_branch['BUSNUM'][i][1]} to {sc_trn_branch['BUSNUM'][i][2]}, Id:{sc_trn_branch['CKT'][i]}":ierr[0]})
                for j in range(3):
                    ierr = self.psspy.three_wnd_winding_data_5(ibus=sc_trn_branch['BUSNUM'][i][0],
                                                        jbus=sc_trn_branch['BUSNUM'][i][1],
                                                        kbus=sc_trn_branch['BUSNUM'][i][2],
                                                        ckt=sc_trn_branch['CKT'][i],
                                                        warg=j+1,
                                                        intgar1=sc_trn_branch['NTAPS'][i][j],
                                                        intgar2=sc_trn_branch['TABLE'][i][j],
                                                        intgar3=sc_trn_branch['CONBUS'][i][j],
                                                        intgar4=sc_trn_branch['NOD'][i][j] if self.version > 34 else 0,
                                                        #   intgar5=,
                                                        intgar6=sc_trn_branch['CNTL'][i][j],
                                                        realari1=sc_trn_branch['WIND'][i][j],
                                                        realari2=sc_trn_branch['NOMV'][i][j],
                                                        realari3=sc_trn_branch['ANG'][i][j],
                                                        realari4=sc_trn_branch['RMAX'][i][j],
                                                        realari5=sc_trn_branch['RMIN'][i][j],
                                                        realari6=sc_trn_branch['VMAX'][i][j],
                                                        realari7=sc_trn_branch['VMIN'][i][j],
                                                        realari8=sc_trn_branch['XFRCMP'][i][j].real,
                                                        realari9=sc_trn_branch['XFRCMP'][i][j].imag,
                                                        realari10=sc_trn_branch['CNXA'][i][j],
                                                        ratings1=sc_trn_branch['RATINGS'][i][j][0],
                                                        ratings2=sc_trn_branch['RATINGS'][i][j][1],
                                                        ratings3=sc_trn_branch['RATINGS'][i][j][2],
                                                        ratings4=sc_trn_branch['RATINGS'][i][j][3],
                                                        ratings5=sc_trn_branch['RATINGS'][i][j][4],
                                                        ratings6=sc_trn_branch['RATINGS'][i][j][5],
                                                        ratings7=sc_trn_branch['RATINGS'][i][j][6],
                                                        ratings8=sc_trn_branch['RATINGS'][i][j][7],
                                                        ratings9=sc_trn_branch['RATINGS'][i][j][8],
                                                        ratings10=sc_trn_branch['RATINGS'][i][j][9],
                                                        ratings11=sc_trn_branch['RATINGS'][i][j][10],
                                                        ratings12=sc_trn_branch['RATINGS'][i][j][11]
                                                        )
                    trn_branch_status.update({f"{sc_trn_branch['BUSNUM'][i][0]} to {sc_trn_branch['BUSNUM'][i][1]} to {sc_trn_branch['BUSNUM'][i][2]} WINDING {j+1}, Ckt:{sc_trn_branch['CKT'][i]}":ierr[0]})
        
        save_trn_branch = os.path.join(directory_to_save_files, save_trn_branch_name)
        self.psspy.save(save_trn_branch)
        # self.psspy.close_powerflow()
        # self.psspy.deltmpfiles()

        return trn_branch_status

    def add_gen(self,small_case,main_case_name,small_case_name,directory_to_save_files):
        save_gen_name = f'{main_case_name}_added_gen_{small_case_name}'
        # self.open_case(**{'sfile' : case_to_use})
        gen_status = OrderedDict()
        sc_gen = small_case.pssgen
        total_gen = len(sc_gen['NUM'])
        gen_status.update(total_gen=total_gen)

        if self.version >= 36.0:
            _func_ = self.psspy.machine_data_5
        elif self.version >= 35.3:
            _func_ = self.psspy.machine_data_4
        elif self.version >= 35.0:
            _func_ = self.psspy.machine_data_3
        elif self.version >= 31.0:
            _func_ = self.psspy.machine_data_2
            

        for i in range(total_gen):
            ierr = self.psspy.plant_data_4(ibus=sc_gen['NUM'][i],
                                    inode=0, 
                                    intgar1=sc_gen['IREG'][i],
                                    intgar2=sc_gen['NREG'][i] if self.version > 34 else 0,
                                    realar1=sc_gen['VS'][i],
                                    realar2=sc_gen['RMPCT'][i]
                                    )

            gen_status.update({f"Plant {sc_gen['NUM'][i]}":ierr})

            if self.version >= 36.0:
                ierr = _func_(ibus=sc_gen['NUM'][i], 
                                        id=sc_gen['IDE'][i], 
                                        intgar1=sc_gen['STAT'][i],
                                        intgar2=sc_gen['OWNER'][i][0],
                                        intgar3=sc_gen['OWNER'][i][1],
                                        intgar4=sc_gen['OWNER'][i][2],
                                        intgar5=sc_gen['OWNER'][i][3],
                                        intgar6=sc_gen['WMOD'][i],
                                        intgar7=sc_gen['BASLOD'][i],
                                        realar1=sc_gen['PG'][i]*100,
                                        realar2=sc_gen['QG'][i]*100,
                                        realar3=sc_gen['QT'][i]*100,
                                        realar4=sc_gen['QB'][i]*100,
                                        realar5=sc_gen['PT'][i]*100,
                                        realar6=sc_gen['PB'][i]*100,
                                        realar7=sc_gen['MBASE'][i],
                                        realar8=sc_gen['ZSORCE'][i].real,
                                        realar9=sc_gen['ZSORCE'][i].imag,
                                        realar10=sc_gen['XTRAN'][i].real,
                                        realar11=sc_gen['XTRAN'][i].imag,
                                        realar12=sc_gen['GTAP'][i],
                                        realar13=sc_gen['OWNPCT'][i][0],
                                        realar14=sc_gen['OWNPCT'][i][1],
                                        realar15=sc_gen['OWNPCT'][i][2],
                                        realar16=sc_gen['OWNPCT'][i][3],
                                        realar17=sc_gen['WPF'][i],
                                        # namear1=,
                                        namear2=sc_gen['MCNAME'][i]
                                        )
            elif self.version >= 31.0:
                ierr = _func_(ibus=sc_gen['NUM'][i], 
                                        id=sc_gen['IDE'][i], 
                                        intgar1=sc_gen['STAT'][i],
                                        intgar2=sc_gen['OWNER'][i][0],
                                        intgar3=sc_gen['OWNER'][i][1],
                                        intgar4=sc_gen['OWNER'][i][2],
                                        intgar5=sc_gen['OWNER'][i][3],
                                        intgar6=sc_gen['WMOD'][i],
                                        # intgar7=sc_gen['BASLOD'][i],
                                        realar1=sc_gen['PG'][i]*100,
                                        realar2=sc_gen['QG'][i]*100,
                                        realar3=sc_gen['QT'][i]*100,
                                        realar4=sc_gen['QB'][i]*100,
                                        realar5=sc_gen['PT'][i]*100,
                                        realar6=sc_gen['PB'][i]*100,
                                        realar7=sc_gen['MBASE'][i],
                                        realar8=sc_gen['ZSORCE'][i].real,
                                        realar9=sc_gen['ZSORCE'][i].imag,
                                        realar10=sc_gen['XTRAN'][i].real,
                                        realar11=sc_gen['XTRAN'][i].imag,
                                        realar12=sc_gen['GTAP'][i],
                                        realar13=sc_gen['OWNPCT'][i][0],
                                        realar14=sc_gen['OWNPCT'][i][1],
                                        realar15=sc_gen['OWNPCT'][i][2],
                                        realar16=sc_gen['OWNPCT'][i][3],
                                        realar17=sc_gen['WPF'][i],
                                        # namear1=,
                                        # namear2=sc_gen['MCNAME'][i]
                                        )
            gen_status.update({f"Gen {sc_gen['NUM'][i]}, Id:{sc_gen['IDE'][i]}":ierr})
        
        save_gen = os.path.join(directory_to_save_files, save_gen_name)    
        self.psspy.save(save_gen)
        # self.psspy.close_powerflow()
        # self.psspy.deltmpfiles()

        return gen_status
    
    
    def modify_gen(self,small_case):
        sc_gen = small_case.pssgen
        total_gen = len(sc_gen['NUM'])

        if self.version >= 36.0:
            _func_ = self.psspy.machine_chng_5
        elif self.version >= 35.3:
            _func_ = self.psspy.machine_chng_4
        elif self.version >= 35.0:
            _func_ = self.psspy.machine_chng_3
        elif self.version >= 31.0:
            _func_ = self.psspy.machine_chng_2
            

        for i in range(total_gen):
            if self.version >= 36.0:
                ierr = _func_(ibus=sc_gen['NUM'][i], 
                                        id=sc_gen['IDE'][i], 
                                        # intgar1=sc_gen['STAT'][i],
                                        # intgar2=sc_gen['OWNER'][i][0],
                                        # intgar3=sc_gen['OWNER'][i][1],
                                        # intgar4=sc_gen['OWNER'][i][2],
                                        # intgar5=sc_gen['OWNER'][i][3],
                                        # intgar6=sc_gen['WMOD'][i],
                                        # intgar7=sc_gen['BASLOD'][i],
                                        # realar1=sc_gen['PG'][i]*100,
                                        realar2=sc_gen['QG'][i]*100,
                                        realar3=sc_gen['QT'][i]*100,
                                        realar4=sc_gen['QB'][i]*100,
                                        # realar5=sc_gen['PT'][i]*100,
                                        # realar6=sc_gen['PB'][i]*100,
                                        # realar7=sc_gen['MBASE'][i],
                                        # realar8=sc_gen['ZSORCE'][i].real,
                                        # realar9=sc_gen['ZSORCE'][i].imag,
                                        # realar10=sc_gen['XTRAN'][i].real,
                                        # realar11=sc_gen['XTRAN'][i].imag,
                                        # realar12=sc_gen['GTAP'][i],
                                        # realar13=sc_gen['OWNPCT'][i][0],
                                        # realar14=sc_gen['OWNPCT'][i][1],
                                        # realar15=sc_gen['OWNPCT'][i][2],
                                        # realar16=sc_gen['OWNPCT'][i][3],
                                        # realar17=sc_gen['WPF'][i],
                                        # # namear1=,
                                        # namear2=sc_gen['MCNAME'][i]
                                        )
            elif self.version >= 31.0:
                ierr = _func_(ibus=sc_gen['NUM'][i], 
                                        id=sc_gen['IDE'][i], 
                                        # intgar1=sc_gen['STAT'][i],
                                        # intgar2=sc_gen['OWNER'][i][0],
                                        # intgar3=sc_gen['OWNER'][i][1],
                                        # intgar4=sc_gen['OWNER'][i][2],
                                        # intgar5=sc_gen['OWNER'][i][3],
                                        # intgar6=sc_gen['WMOD'][i],
                                        # # intgar7=sc_gen['BASLOD'][i],
                                        # realar1=sc_gen['PG'][i]*100,
                                        realar2=sc_gen['QG'][i]*100,
                                        realar3=sc_gen['QT'][i]*100,
                                        realar4=sc_gen['QB'][i]*100,
                                        # realar5=sc_gen['PT'][i]*100,
                                        # realar6=sc_gen['PB'][i]*100,
                                        # realar7=sc_gen['MBASE'][i],
                                        # realar8=sc_gen['ZSORCE'][i].real,
                                        # realar9=sc_gen['ZSORCE'][i].imag,
                                        # realar10=sc_gen['XTRAN'][i].real,
                                        # realar11=sc_gen['XTRAN'][i].imag,
                                        # realar12=sc_gen['GTAP'][i],
                                        # realar13=sc_gen['OWNPCT'][i][0],
                                        # realar14=sc_gen['OWNPCT'][i][1],
                                        # realar15=sc_gen['OWNPCT'][i][2],
                                        # realar16=sc_gen['OWNPCT'][i][3],
                                        # realar17=sc_gen['WPF'][i],
                                        # namear1=,
                                        # namear2=sc_gen['MCNAME'][i]
                                        )
            

    def add_fixed_shunt(self,small_case,main_case_name,small_case_name,directory_to_save_files):
        save_fsh_name = f'{main_case_name}_added_fixed_shunt_{small_case_name}'
        # self.open_case(**{'sfile' : case_to_use})
        fsh_status = OrderedDict()
        sc_fsh = small_case.pssfsh
        total_fsh = len(sc_fsh['NUM'])
        fsh_status.update(total_fsh=total_fsh)

        if self.version >= 36.0:
            _func_ = self.psspy.shunt_data_2
        elif self.version >= 31.0:
            _func_ = self.psspy.shunt_data

        for i in range(total_fsh):
            ierr = _func_(ibus=sc_fsh['NUM'][i], 
                                    id=sc_fsh['ID'][i], 
                                    intgar1=sc_fsh['STATUS'][i],
                                    realar1=sc_fsh['SHUNT'][i].real*100,
                                    realar2=sc_fsh['SHUNT'][i].imag*100,
                                    #   shname=sc_fsh[''][i]
                                    )
            fsh_status.update({f"Fixed Shunt {sc_fsh['NUM'][i]}, Id:{sc_fsh['ID'][i]}":ierr})
        
        save_fsh = os.path.join(directory_to_save_files, save_fsh_name)
        self.psspy.save(save_fsh)
        # self.psspy.close_powerflow()
        # self.psspy.deltmpfiles()

        return fsh_status


    def add_switched_shunt(self,small_case,main_case_name,small_case_name,directory_to_save_files):
        save_swsh_name = f'{main_case_name}_added_switched_shunt_{small_case_name}'
        # self.open_case(**{'sfile' : case_to_use})
        swsh_status = OrderedDict()
        sc_swsh = small_case.psswsh
        total_swsh = len(sc_swsh['NUM'])
        swsh_status.update(total_swsh=total_swsh)

        if self.version >= 36.0:
            _func_ = self.psspy.switched_shunt_data_6
        elif self.version >= 35.0:
            _func_ = self.psspy.switched_shunt_data_5
        elif self.version >= 34.4:
            _func_ = self.psspy.switched_shunt_data_4

        for i in range(total_swsh):
            if self.version >= 36.0:
                ierr = _func_(ibus=sc_swsh['NUM'][i],
                                            id=sc_swsh['ID'][i],
                                            intgar1=sc_swsh['NI'][i][0],
                                            intgar2=sc_swsh['NI'][i][1],
                                            intgar3=sc_swsh['NI'][i][2],
                                            intgar4=sc_swsh['NI'][i][3],
                                            intgar5=sc_swsh['NI'][i][4],
                                            intgar6=sc_swsh['NI'][i][5],
                                            intgar7=sc_swsh['NI'][i][6],
                                            intgar8=sc_swsh['NI'][i][7],
                                            intgar9=sc_swsh['MODSW'][i],
                                            intgar10=sc_swsh['SWREM'][i],
                                            intgar11=sc_swsh['SWNOD'][i],
                                            intgar12=sc_swsh['STAT'][i],
                                            intgar13=sc_swsh['ADJM'][i],
                                            intgar14=sc_swsh['SI'][i][0],
                                            intgar15=sc_swsh['SI'][i][1],
                                            intgar16=sc_swsh['SI'][i][2],
                                            intgar17=sc_swsh['SI'][i][3],
                                            intgar18=sc_swsh['SI'][i][4],
                                            intgar19=sc_swsh['SI'][i][5],
                                            intgar20=sc_swsh['SI'][i][6],
                                            intgar21=sc_swsh['SI'][i][7],
                                            realar1=sc_swsh['BI'][i][0]*100,
                                            realar2=sc_swsh['BI'][i][1]*100,
                                            realar3=sc_swsh['BI'][i][2]*100,
                                            realar4=sc_swsh['BI'][i][3]*100,
                                            realar5=sc_swsh['BI'][i][4]*100,
                                            realar6=sc_swsh['BI'][i][5]*100,
                                            realar7=sc_swsh['BI'][i][6]*100,
                                            realar8=sc_swsh['BI'][i][7]*100,
                                            realar9=sc_swsh['VSWHI'][i],
                                            realar10=sc_swsh['VSWLO'][i],
                                            realar11=sc_swsh['BINIT'][i],
                                            realar12=sc_swsh['RMPCT'][i],
                                            swsnam=sc_swsh['SWNAME'][i]
                                            )
            elif self.version >= 35.0:
                ierr = _func_(ibus=sc_swsh['NUM'][i],
                                            id=sc_swsh['ID'][i],
                                            intgar1=sc_swsh['NI'][i][0],
                                            intgar2=sc_swsh['NI'][i][1],
                                            intgar3=sc_swsh['NI'][i][2],
                                            intgar4=sc_swsh['NI'][i][3],
                                            intgar5=sc_swsh['NI'][i][4],
                                            intgar6=sc_swsh['NI'][i][5],
                                            intgar7=sc_swsh['NI'][i][6],
                                            intgar8=sc_swsh['NI'][i][7],
                                            intgar9=sc_swsh['MODSW'][i],
                                            intgar10=sc_swsh['SWREM'][i],
                                            intgar11=sc_swsh['SWNOD'][i],
                                            intgar12=sc_swsh['STAT'][i],
                                            intgar13=sc_swsh['ADJM'][i],
                                            intgar14=sc_swsh['SI'][i][0],
                                            intgar15=sc_swsh['SI'][i][1],
                                            intgar16=sc_swsh['SI'][i][2],
                                            intgar17=sc_swsh['SI'][i][3],
                                            intgar18=sc_swsh['SI'][i][4],
                                            intgar19=sc_swsh['SI'][i][5],
                                            intgar20=sc_swsh['SI'][i][6],
                                            intgar21=sc_swsh['SI'][i][7],
                                            realar1=sc_swsh['BI'][i][0]*100,
                                            realar2=sc_swsh['BI'][i][1]*100,
                                            realar3=sc_swsh['BI'][i][2]*100,
                                            realar4=sc_swsh['BI'][i][3]*100,
                                            realar5=sc_swsh['BI'][i][4]*100,
                                            realar6=sc_swsh['BI'][i][5]*100,
                                            realar7=sc_swsh['BI'][i][6]*100,
                                            realar8=sc_swsh['BI'][i][7]*100,
                                            realar9=sc_swsh['VSWHI'][i],
                                            realar10=sc_swsh['VSWLO'][i],
                                            realar11=sc_swsh['BINIT'][i],
                                            realar12=sc_swsh['RMPCT'][i],
                                            # swsnam=sc_swsh['SWNAME'][i]
                                            )
            elif self.version >= 34.4:
                ierr = _func_(ibus=sc_swsh['NUM'][i],
                                            id=sc_swsh['ID'][i],
                                            intgar1=sc_swsh['NI'][i][0],
                                            intgar2=sc_swsh['NI'][i][1],
                                            intgar3=sc_swsh['NI'][i][2],
                                            intgar4=sc_swsh['NI'][i][3],
                                            intgar5=sc_swsh['NI'][i][4],
                                            intgar6=sc_swsh['NI'][i][5],
                                            intgar7=sc_swsh['NI'][i][6],
                                            intgar8=sc_swsh['NI'][i][7],
                                            intgar9=sc_swsh['MODSW'][i],
                                            intgar10=sc_swsh['SWREM'][i],
                                            intgar11=sc_swsh['SWNOD'][i],
                                            intgar12=sc_swsh['STAT'][i],
                                            intgar13=sc_swsh['ADJM'][i],
                                            intgar14=sc_swsh['SI'][i][0],
                                            # intgar15=sc_swsh['SI'][i][1],
                                            # intgar16=sc_swsh['SI'][i][2],
                                            # intgar17=sc_swsh['SI'][i][3],
                                            # intgar18=sc_swsh['SI'][i][4],
                                            # intgar19=sc_swsh['SI'][i][5],
                                            # intgar20=sc_swsh['SI'][i][6],
                                            # intgar21=sc_swsh['SI'][i][7],
                                            realar1=sc_swsh['BI'][i][0]*100,
                                            realar2=sc_swsh['BI'][i][1]*100,
                                            realar3=sc_swsh['BI'][i][2]*100,
                                            realar4=sc_swsh['BI'][i][3]*100,
                                            realar5=sc_swsh['BI'][i][4]*100,
                                            realar6=sc_swsh['BI'][i][5]*100,
                                            realar7=sc_swsh['BI'][i][6]*100,
                                            realar8=sc_swsh['BI'][i][7]*100,
                                            realar9=sc_swsh['VSWHI'][i],
                                            realar10=sc_swsh['VSWLO'][i],
                                            realar11=sc_swsh['BINIT'][i],
                                            realar12=sc_swsh['RMPCT'][i],
                                            # swsnam=sc_swsh['SWNAME'][i]
                                            )
            swsh_status.update({f"Fixed Shunt {sc_swsh['NUM'][i]}, Id:{sc_swsh['ID'][i]}":ierr})
        
        save_swsh = os.path.join(directory_to_save_files, save_swsh_name)
        self.psspy.save(save_swsh)
        # self.psspy.close_powerflow()
        # self.psspy.deltmpfiles()

        return swsh_status
        

    def add_load(self,small_case,main_case_name,small_case_name,directory_to_save_files):
        save_lod_name = f'{main_case_name}_added_load_{small_case_name}'
        # self.open_case(**{'sfile' : case_to_use})
        lod_status = OrderedDict()
        sc_lod = small_case.psslod
        total_lod = len(sc_lod['NUM'])
        lod_status.update(total_lod=total_lod)

        if self.version >= 36.0:
            _func_ = self.psspy.load_data_7
        elif self.version >= 35.0:
            _func_ = self.psspy.load_data_6
        elif self.version >= 34.4:
            _func_ = self.psspy.load_data_5

        for i in range(total_lod):
            if self.version >= 36.0:
                ierr = _func_(ibus=sc_lod['NUM'][i], 
                                    id=sc_lod['ID'][i], 
                                    intgar1=sc_lod['STATUS'][i],
                                    intgar2=sc_lod['AREA'][i],
                                    intgar3=sc_lod['ZONE'][i],
                                    intgar4=sc_lod['OWNER'][i],
                                    intgar5=sc_lod['LDSCALE'][i],
                                    intgar6=sc_lod['LDINT'][i],
                                    intgar7=sc_lod['DGENM'][i],
                                    realar1=sc_lod['LOAD'][i][0].real*100,
                                    realar2=sc_lod['LOAD'][i][0].imag*100,
                                    realar3=sc_lod['LOAD'][i][1].real*100,
                                    realar4=sc_lod['LOAD'][i][1].imag*100,
                                    realar5=sc_lod['LOAD'][i][2].real*100,
                                    realar6=sc_lod['LOAD'][i][2].imag*100,
                                    realar7=sc_lod['DGENPQ'][i].real*100,
                                    realar8=sc_lod['DGENPQ'][i].imag*100,
                                    #  lodtyp=sc_lod[''][i],
                                    ldname=sc_lod['LDNAME'][i]
                                    )
            elif self.version >= 34.0:
                ierr = _func_(ibus=sc_lod['NUM'][i], 
                                    id=sc_lod['ID'][i], 
                                    intgar1=sc_lod['STATUS'][i],
                                    intgar2=sc_lod['AREA'][i],
                                    intgar3=sc_lod['ZONE'][i],
                                    intgar4=sc_lod['OWNER'][i],
                                    intgar5=sc_lod['LDSCALE'][i],
                                    intgar6=sc_lod['LDINT'][i],
                                    intgar7=sc_lod['DGENM'][i],
                                    realar1=sc_lod['LOAD'][i][0].real*100,
                                    realar2=sc_lod['LOAD'][i][0].imag*100,
                                    realar3=sc_lod['LOAD'][i][1].real*100,
                                    realar4=sc_lod['LOAD'][i][1].imag*100,
                                    realar5=sc_lod['LOAD'][i][2].real*100,
                                    realar6=sc_lod['LOAD'][i][2].imag*100,
                                    realar7=sc_lod['DGENPQ'][i].real*100,
                                    realar8=sc_lod['DGENPQ'][i].imag*100,
                                    #  lodtyp=sc_lod[''][i],
                                    # ldname=sc_lod['LDNAME'][i]
                                    )
            lod_status.update({f"Load {sc_lod['NUM'][i]}, Id:{sc_lod['ID'][i]}":ierr})
        
        save_lod = os.path.join(directory_to_save_files, save_lod_name)
        self.psspy.save(save_lod)
        # self.psspy.close_powerflow()
        # self.psspy.deltmpfiles()

        return lod_status
        
        
    def add_induction_machine(self,small_case,main_case_name,small_case_name,directory_to_save_files):
        save_ind_name = f'{main_case_name}_added_ind_{small_case_name}'
        # self.open_case(**{'sfile' : case_to_use})
        ind_status = OrderedDict()
        sc_ind = small_case.pssind
        total_ind = len(sc_ind['NUM'])
        ind_status.update(total_ind=total_ind)

        if self.version >= 36.0:
            _func_ = self.psspy.induction_machine_data_2
        elif self.version >= 33.0:
            _func_ = self.psspy.induction_machine_data

        for i in range(total_ind):
            if self.version >= 36.0:
                ierr = _func_(ibus=sc_ind['NUM'][i], 
                                                id=sc_ind['ID'][i], 
                                                intgar1=sc_ind['STATUS'][i],
                                                intgar2=sc_ind['SCODE'][i],
                                                intgar3=sc_ind['DCODE'][i],
                                                intgar4=sc_ind['AREA'][i],
                                                intgar5=sc_ind['ZONE'][i],
                                                intgar6=sc_ind['OWNER'][i],
                                                intgar7=sc_ind['TCODE'][i],
                                                intgar8=sc_ind['BCODE'][i],
                                                intgar9=sc_ind['PCODE'][i],
                                                realar1=sc_ind['MBASE'][i],
                                                realar2=sc_ind['RATEKV'][i],
                                                realar3=sc_ind['PSET'][i],
                                                realar4=sc_ind['H'][i],
                                                realar5=sc_ind['A'][i],
                                                realar6=sc_ind['B'][i],
                                                realar7=sc_ind['D'][i],
                                                realar8=sc_ind['E'][i],
                                                realar9=sc_ind['RA'][i],
                                                realar10=sc_ind['XA'][i],
                                                realar11=sc_ind['XM'][i],
                                                realar12=sc_ind['R1'][i],
                                                realar13=sc_ind['X1'][i],
                                                realar14=sc_ind['R2'][i],
                                                realar15=sc_ind['X2'][i],
                                                realar16=sc_ind['X3'][i],
                                                realar17=sc_ind['E1'][i],
                                                realar18=sc_ind['SE1'][i],
                                                realar19=sc_ind['E2'][i],
                                                realar20=sc_ind['SE2'][i],
                                                realar21=sc_ind['IA1'][i],
                                                realar22=sc_ind['IA2'][i],
                                                realar23=sc_ind['IAM'][i],
                                                indnamear=sc_ind['IMNAME'][i]
                                                )
            elif self.version >= 33.0:
                ierr = _func_(ibus=sc_ind['NUM'][i], 
                                                id=sc_ind['ID'][i], 
                                                intgar1=sc_ind['STATUS'][i],
                                                intgar2=sc_ind['SCODE'][i],
                                                intgar3=sc_ind['DCODE'][i],
                                                intgar4=sc_ind['AREA'][i],
                                                intgar5=sc_ind['ZONE'][i],
                                                intgar6=sc_ind['OWNER'][i],
                                                intgar7=sc_ind['TCODE'][i],
                                                intgar8=sc_ind['BCODE'][i],
                                                intgar9=sc_ind['PCODE'][i],
                                                realar1=sc_ind['MBASE'][i],
                                                realar2=sc_ind['RATEKV'][i],
                                                realar3=sc_ind['PSET'][i],
                                                realar4=sc_ind['H'][i],
                                                realar5=sc_ind['A'][i],
                                                realar6=sc_ind['B'][i],
                                                realar7=sc_ind['D'][i],
                                                realar8=sc_ind['E'][i],
                                                realar9=sc_ind['RA'][i],
                                                realar10=sc_ind['XA'][i],
                                                realar11=sc_ind['XM'][i],
                                                realar12=sc_ind['R1'][i],
                                                realar13=sc_ind['X1'][i],
                                                realar14=sc_ind['R2'][i],
                                                realar15=sc_ind['X2'][i],
                                                realar16=sc_ind['X3'][i],
                                                realar17=sc_ind['E1'][i],
                                                realar18=sc_ind['SE1'][i],
                                                realar19=sc_ind['E2'][i],
                                                realar20=sc_ind['SE2'][i],
                                                realar21=sc_ind['IA1'][i],
                                                realar22=sc_ind['IA2'][i],
                                                realar23=sc_ind['IAM'][i],
                                                # indnamear=sc_ind['IMNAME'][i]
                                                )
            ind_status.update({f"Load {sc_ind['NUM'][i]}, Id:{sc_ind['ID'][i]}":ierr})
        
        save_ind = os.path.join(directory_to_save_files, save_ind_name)
        self.psspy.save(save_ind)
        # self.psspy.close_powerflow()
        # self.psspy.deltmpfiles()

        return ind_status



    def get_gen_dict(self,small_case):
        
        gen_dict = OrderedDict()
        sc_gen = small_case.pssgen
        total_gen = len(sc_gen['NUM'])
        
        
        for i in range(total_gen):
            kwargs = { 'bus'    :    sc_gen['NUM'][i], 
                                'id'      :    sc_gen['IDE'][i], 
                                'status'  :    sc_gen['STAT'][i],
                                'pgen'    :    sc_gen['PG'][i]*100,
                                'qgen'    :    sc_gen['QG'][i]*100,
                                'qmax'    :    sc_gen['QT'][i]*100,
                                'qmin'    :    sc_gen['QB'][i]*100,
                                'pmax'    :    sc_gen['PT'][i]*100,
                                'pmin'    :    sc_gen['PB'][i]*100,
                                'mbase'   :    sc_gen['MBASE'][i],
                                'mbase'   :    sc_gen['MBASE'][i],
                            }
            
            if self.version > 36.0:
                kwargs.update({'name'   :    sc_gen['MCNAME'][i]})
                
            gen_dict[i] = kwargs
        return gen_dict