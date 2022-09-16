#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    OpenBabel Python Interface v1.0.3
    \n
    This module allows you to run OpenBabel CLI commands in python.
    
    .. include:: ./README.md
"""

############ AUTHOURSHIP & COPYRIGHTS ############
__author__      = "Abdullrahman Elsayed"
__copyright__   = "Copyright 2022, Abdullrahman Elsayed"
__credits__     = "Abdullrahman Elsayed"
__license__     = "MIT"
__version__     = "1.0.3"
__maintainer__  = "Abdullrahman Elsayed"
__email__       = "abdull15199@gmail.com"
__status__      = "Production"
__doc__         = "This module allows you to run OpenBabel CLI commands in python."
##################################################

import os, subprocess, inspect, tempfile, sys, time
# from openbabel import openbabel, pybel

class IOHandler:
    def UsrIn(self, DisplayText : str, InType = "Text") -> str:
        """
            Format user input

            Args:
                DisplayText (str): Text to be displayed on user input
                InType (str, optional): Text, Path. Defaults to "Text"

            Returns:
                str: Formatted text
        """

        input_value = input(DisplayText)

        if InType == "Text":
            return input_value
        elif InType == "Path":
            return input_value.replace("\\", "/").rstrip("/")
        elif InType == "Intger":
            return int(0) if input_value == "" or input_value.isalpha() else int(input_value)
        
    def UsrOut(self, DisplayText : str, Colour = "Default", Status = "", Print = True, StartBreak = False, EndBreak = False, PSL = False, SysInit = False) -> str or None:
        """
            Format output text

            Args:
                DisplayText (str): Text to be displayed.
                Colour (str, optional): Text colour [may use light (l) or dark (d)]. Defaults to "Dark-Black".
                Status (str, optional): Options [Error: "ERR", Success: "SCS", Note: "NTE"]. Defaults to "".
                Print (bool, optional): Set True to print the output text, False to return it. Defaults to True.
                StartBreak (bool, optional): Set True to break line before text. Defaults to False.
                EndBreak (bool, optional): Set True to break line after text. Defaults to False.
                SysInit (bool, optional): Set True if os.system() was not called. Defaults to False.

            Returns:
                str or None: Formatted text
        """

        # Initiating os.system() is a MUST for colours to be displaied.
        if SysInit: os.system("color 00")

        # Detecting colour intensity (Light | Dark)
        if Colour.lower() == 'default':
            Colour = None
            Intense = True
        elif "-" in Colour.lower():
            Colour = Colour.split("-")[-1].lower()
            Intense = Colour.split("-")[0][0].lower() == "d"
        else:
            Colour = Colour.lower()
            Intense = True

        Txt = str(DisplayText)
        Intensity = "3" if Intense else "9"
        ESC = "\033" or "\u001b"
        END = ESC + "[0m"

        ColourCodes = dict({
            "black"  : "0m",
            "red"    : "1m",
            "green"  : "2m",
            "yellow" : "3m",
            "blue"   : "4m",
            "magenta": "5m",
            "cyan"   : "6m",
            "white"  : "7m"
        })

        if   Status == "ERR": Txt = f"{ESC}[{Intensity}{ColourCodes['red']}ERROR: {Txt}{END}"
        elif Status == "SCS": Txt = f"{ESC}[{Intensity}{ColourCodes['green']}SUCCESS: {Txt}{END}"
        elif Status == "NTE": Txt = f"{ESC}[{Intensity}{ColourCodes['yellow']}NOTE: {Txt}{END}"
        elif Status == "PRC": Txt = f"{ESC}[{Intensity}{ColourCodes['blue']}PROCEEDING: {Txt}{END}"
        elif Colour == None : Txt = Txt
        else: Txt = f"{ESC}[{Intensity}{ColourCodes[Colour]}{Txt}{END}"
        
        Txt = "\n" + Txt if StartBreak else Txt
        Txt = Txt + "\n" if EndBreak else Txt

        if Print == True:
            self.PSL(Txt) if PSL else print(Txt)
        else:
            return Txt

    # Print In The Same Line
    def PSL(self, Text : str) -> None:
        """
            Print on the same line

            Args:
                Text (str): Text to be printed
        """

        sys.stdout.write("\r\033[K" + Text)

    # Print With Typing Effect
    def TypeText(self, Text : str, Delay = 0.001) -> None:
        """
            Print text with typing effect

            Args:
                Text (str): Text to be typed
                Delay (float, optional): Letter by letter print delay. Defaults to 0.001.
        """

        for ch in Text:
            sys.stdout.write(ch)  # Writes Letters
            sys.stdout.flush()   # Flushes Written Letters
            time.sleep(Delay)     # Delay Before Adding New Letter To Text

    # Print Centered Text
    def CenterText(self, Text : str, Width = 100, Spacer = " ") -> str:
        """
            Center text in sys.stdout window

            Args:
                Text (str): Text to be centered
                Width (int, optional): Window width. Defaults to 100.
                Spacer (str, optional): Width spacer. Defaults to " ".

            Returns:
                str: Centered text
        """

        return str(Text).center(Width, Spacer)

    ####### LEGACY SUPPORT #######
    # CLEANES STRING FROM SPECEFIED CHARECTERS
    def CleanStr(self, Text: str, Symbols: str or list, Type = "Text", IgnoreNonASCII = False):
        if IgnoreNonASCII:
            Text = Text.encode().decode("ASCII", "ignore")
        else:
            pass

        if Type == "Path":
            Text = Text.replace("\\", "/").rstrip("/") + "/"
            Symbols = list('\\*"<>|')
            
        elif Type == "FileName":
            Symbols = list('\\/*:"<>|')

        else:
            pass
        
        for symb in Symbols: Text = Text.replace(symb, "")
        return Text

    # Splits path into file tree
    def FileTree(self, Path: str) -> dict:
        splitted_path = Path.replace("\\", "/").split("/")
        root = "/".join(splitted_path[:-1]) + "/"
        fullname = splitted_path[-1]
        name = ".".join(fullname.split(".")[:-1])
        extension = "." + fullname.split(".")[-1]

        return {
            "Root": root,
            "Fullname": fullname,
            "Name": name,
            "Extension": extension,
        }

class OpenBabel(IOHandler):
    """
        Main class of the module.

        Inheritance:
            IOHandler (class): Parent class.
    """
    
    def __init__(self) -> None:
        # Prefix messages to be displayed on shell output to indicate
        ## which software is running and writing these messages to stdout
        prefix_style = lambda Text: self.UsrOut(DisplayText=Text, Colour='Yellow', Print=None)
        self.ShellDisplayPrefix = {
            'Shell'     : prefix_style('SHELL >>> '),
            'OpenBabel' : prefix_style('OpenBabel >>> '),
        }

        # Executables Paths (__ExcPth) contains executable software paths
        self.__ExcPth = {
            'Obabel'        : 'obabel',
            'Obminimize'    : 'obminimize',
            'Obconformer'   : 'obconformer',
            'Obenergy'      : 'obenergy',
            'Obgen'         : 'obgen',
        }

        # Command Set (__CmdSet) contains reorganized commands identifiers
        self.__CmdSet = {
            'Obabel'        : {
                'AddHydrogen'               : lambda condition      : f'-h' if condition else '',                   # -h 	Add hydrogens (make all hydrogen explicit)
                'AddProperty'               : lambda name, value    : f'--property {name} {value}',                 # --property <name value> Add or replace a property (for example, in an SD file)
                'AddProps'                  : lambda props          : f'--add {" ".join(props)}',                   # --add <comma sep list> Add properties (for SDF, CML, etc.) from descriptors in list. Use -L descriptors to see available descriptors.
                'Center'                    : lambda condition      : f'-c' if condition else '',                   # -c 	Center atomic coordinates at (0,0,0)
                'ChargeCalcMethod'          : lambda method         : f'--partialcharge {method}',                  # --partialcharge <charge-method> Calculate partial charges by the specified method. List available methods using obabel -L charges.
                'CombineConformers'         : lambda condition      : f'--readconformers' if condition else '',     # --readconformers Combine adjacent conformers in multi-molecule input into a single molecule
                'ConvertDative'             : lambda condition      : f'-b' if condition else '',                   # -b 	Convert dative bonds (e.g. [N+]([O-])=O to N(=O)=O)
                'DeleteHydrogens'           : lambda condition      : f'-d' if condition else '',                   # -d 	Delete hydrogens (make all hydrogen implicit)
                'Generate2D'                : lambda condition      : f'--gen2d' if condition else '',              # --gen2d 	Generate 2D coordinates
                'Generate3D'                : lambda condition      : f'--gen3d' if condition else '',              # --gen3d 	Generate 3D coordinates
                'InputFile'                 : lambda path           : f'"{path}"',                                  # MUST BE KEPT THIS WAY TO ALLOW PASSING INPUT PATH TO 'self.__ExecuteCommand' AS AN ARGUMENT AND VALUE
                'InputFormat'               : lambda in_format      : f'-i {in_format}',                            # -i <format-ID> 	Specifies input format. See Supported File Formats and Options.
                'JoinAllToOneFile'          : lambda condition      : f'-j' if condition else '',                   # -j, --join 	Join all input molecules into a single output molecule entry
                'OutputFile'                : lambda path           : f'-O "{path}"',                               # -O    Specifies output file path
                'OutputFormat'              : lambda out_format     : f'-o {out_format}',                           # -o <format-ID> 	Specifies output format. See Supported File Formats and Options.
                'pH'                        : lambda ph             : f'-p {ph}',                                   # -p <pH> 	Add hydrogens appropriate for pH (use transforms in phmodel.txt)
                'RenameMolecule'            : lambda title          : f'--title "{title}"',                         # --title <title> Add or replace molecular title
                'SaveSeparateConformers'    : lambda condition      : f'--writeconformers' if condition else '',    # --writeconformers Output multiple conformers as separate molecules
                'SaveSeparateFiles'         : lambda condition      : f'-m' if condition else '',                   # -m 	Produce multiple output files, to allow: Splitting one input file - put each molecule into consecutively numbered output files. Batch conversion - convert each of multiple input files into a specified output format
                'SearchConformers'          : lambda options        : f'--conformer {options}',                     # --conformer <options> Conformer searching to generate low-energy or diverse conformers. For more information, see Generating conformers for structures.
                'SeparateFragments'         : lambda condition      : f'--separate' if condition else '',           # --separate 	Separate disconnected fragments into individual molecular records
                'SkipConversionError'       : lambda condition      : f'-e' if condition else '',                   # -e 	Continue to convert molecules after errors
                # '' : lambda             : f'-a',                            # -a <options> 	Format-specific input options. Use -H <format-ID> to see options allowed by a particular format, or see the appropriate section in Supported File Formats and Options.
                # '' : lambda             : f'--addinindex',                  # --addinindex 	Append input index to title (that is, the index before any filtering)
                # '' : lambda             : f'--addoutindex',                 # --addoutindex 	Append output index to title (that is, the index after any filtering)
                # '' : lambda             : f'--addtotitle',                  # --addtotitle <text> Append the text after each molecule title
                # '' : lambda             : f'--append',                      # --append <list> Append properties or descriptor values appropriate for a molecule to its title. For more information, see Append property values to the title.
                # '' : lambda             : f'-C',                            # -C 	Combine molecules in first file with others having the same name
                # '' : lambda             : f'--delete',                      # --delete <list> Delete properties in list
                # '' : lambda             : f'-f',                            # -f <#> 	For multiple entry input, start import with molecule # as the first entry
                # '' : lambda             : f'--filter',                      # --filter <criteria> Filter based on molecular properties. See Filtering molecules from a multimolecule file for examples and a list of criteria.
                # '' : lambda             : f'-k',                            # -k 	Translate computational chemistry modeling keywords. See the computational chemistry formats (Computational chemistry formats), for example GAMESS Input (inp, gamin) and Gaussian 98/03 Input (gjf, gjc, gau, com).
                # '' : lambda             : f'-l',                            # -l <#> 	For multiple entry input, stop import with molecule # as the last entry
                # '' : lambda             : f'-r',                            # -r 	Remove all but the largest contiguous fragment (strip salts)
                # '' : lambda             : f'-s',                            # -s <SMARTS> 	Convert only molecules matching the SMARTS pattern specified
                # '' : lambda             : f'-s',                            # -s <filename.xxx> Convert only molecules with the molecule in the file as a substructure
                # '' : lambda             : f'--sort',                        # --sort 	Output molecules ordered by the value of a descriptor. See Sorting molecules.
                # '' : lambda             : f'--unique',                      # --unique, --unique <param> Do not convert duplicate molecules. See Remove duplicate molecules.
                # '' : lambda             : f'-x',                            # -x <options> 	Format-specific output options. use -H <format-ID> to see options allowed by a particular format, or see the appropriate section in Supported File Formats and Options.
                # '' : lambda             : f'-v',                            # -v <SMARTS> 	Convert only molecules NOT matching the SMARTS pattern specified
                # '' : lambda             : f'-z',                            # -z 	Compress the output with gzip (not on Windows)
            },
            'Obminimize'    : {
                'Typical': \
                    lambda InFile, OutFile, OutFormat, AddHydrogen, Algorithm, MinSteps, ForceField: \
                        f'-n {MinSteps} -ff {ForceField} -{Algorithm} {"-h" if AddHydrogen else ""} -o {OutFormat} "{InFile}" > "{OutFile}"'.strip(),

                'InputFile'                 : lambda path           : f'"{path}"',                      # MUST BE KEPT THIS WAY TO ALLOW PASSING INPUT PATH TO 'self.__ExecuteCommand' AS AN ARGUMENT AND VALUE
                'OutputFile'                : lambda path           : f'> "{path}"',                    # >    Specifies output file path
                'OutputFormat'              : lambda out_format     : f'-o {out_format}',               # -o <format-ID> 	Specifies output format. See Supported File Formats and Options.
                'AddHydrogen'               : lambda condition      : f'-h' if condition else '',       # -h 	Add hydrogens (make all hydrogen explicit)
                'ForceField'                : lambda force_field    : f'-ff {force_field}',             # -ff Forcefield used for minimization
                'MinimizationAlgorithm'     : lambda algorithm      : f'-{algorithm.lower()}',
                'MinimizationSteps'         : lambda n              : f'-n {n}',
            },
            'Obconformer'   : {
                'Typical': \
                    lambda InFile, OutFile, NConfs, MinSteps, ForceField: \
                        f'{NConfs} {MinSteps} "{InFile}" > "{OutFile}" {ForceField}'.strip(),
                
                'InputFile'                 : lambda path           : f'"{path}"',                      # MUST BE KEPT THIS WAY TO ALLOW PASSING INPUT PATH TO 'self.__ExecuteCommand' AS AN ARGUMENT AND VALUE
                'OutputFile'                : lambda path           : f'> "{path}"',                    # >    Specifies output file path
                'ForceField'                : lambda force_field    : f'{force_field}',
                'NumberOfConformers'        : lambda num            : f'{num}',
                'MinimizationSteps'         : lambda n              : f'{n}',
            },
            'Obenergy'      : {
                'Typical': \
                    lambda InFile, OutFile, ForceField, AddHydrogen, Verbose: \
                        f'{"-h" if AddHydrogen else ""} -ff {ForceField} {"-v" if Verbose else ""} "{InFile}" > "{OutFile}"'.strip(),

                'InputFile'                 : lambda path           : f'"{path}"',                      # MUST BE KEPT THIS WAY TO ALLOW PASSING INPUT PATH TO 'self.__ExecuteCommand' AS AN ARGUMENT AND VALUE
                'OutputFile'                : lambda path           : f'> "{path}"',                    # >    Specifies output file path
                'AddHydrogen'               : lambda condition      : f'-h' if condition else '',       # -h 	Add hydrogens (make all hydrogen explicit)
                'ForceField'                : lambda force_field    : f'-ff {force_field}',             # -ff forcefield    Select the forcefield  
                'Verbose'                   : lambda condition      : f'-v' if condition else '',       # -v    Verbose: print out all individual energy interactions
            },
            'Obgen'         : {
                'Typical': \
                    lambda InFile, OutFile, ForceField: \
                        f'-ff {ForceField} "{InFile}" > "{OutFile}"'.strip(),
                
                'InputFile'                 : lambda path           : f'"{path}"',                      # MUST BE KEPT THIS WAY TO ALLOW PASSING INPUT PATH TO 'self.__ExecuteCommand' AS AN ARGUMENT AND VALUE
                'OutputFile'                : lambda path           : f'> "{path}"',                    # >    Specifies output file path
                'ForceField'                : lambda force_field    : f'-ff {force_field}',             # -ff Forcefield used for minimization
            },
        }

    def __ExecuteCommand(self,
        Command:        str,
        ExecName:       str     = 'Shell',
        ExplicitShell:  bool    = True,
        Verbose:        bool    = False,
        ForceVerbose:   bool    = False,
        PrintSameLine:  bool    = False
    ) -> dict:
        """
            ### Execute certain commands in OS shell

            #### Args:
                - Command (str): STRING command to execute. (LIST COMMANDS WILL RAISE ERRORS)
                - ExecName (str, optional): Executable name that excutes the given command. Defaults to 'Shell'.
                - ExplicitShell (bool, optional): Set to True to initiate explicit shell to run the given command \
                    or set to False to run the given command in the current subprocess shell. Defaults to True.
                - Verbose (bool, optional): Set to True to tell you what is going on. Defaults to False.
                - ForceVerbose (bool, optional): If True, will force display outputs usually hidden when directed to a file. e.g. `command > file`. Defaults to False.
                - PrintSameLine (bool, optional): Prints process output on the same line. Defaults to False.
                #### `ForceVerbose` will not work if `Verbose` is False.

            #### Returns:
                - dict: Contain process data. Possible keys are [OutMsg, ErrMsg, ExitCode].
        """

        # If 'Verbose' and 'ForceVerbose' are True, don't re-direct command output to user specified file,
        # collect command output from stdout then eventually write it to the desired file
        if  bool(Verbose) \
        and bool(ForceVerbose):
            # Get dumper sign (either '>' for write, or '>>' for append)
            dumper = '>' if ('>' in Command) else '>>' if ('>>' in Command) else None

            # Check if 'Command' has a dumper, else, no need for anything
            if bool(dumper != None):
                # Split command by the dumper
                Command, __OutFile = Command.split(dumper)
                # Strip endings from above vars
                Command = Command.strip()
                __OutFile = __OutFile.strip().strip('"').strip("'")
            else:
                pass
        
        # Set default std PIPE
        stdpipe = subprocess.PIPE

        # Initiate a process with Popen
        process = subprocess.Popen(args=Command, shell=ExplicitShell, stdin=stdpipe, stdout=stdpipe, stderr=subprocess.STDOUT)
        
        # Making a varable to hold stdout data throughout the process
        STDout = []

        # While loop to be executed to live print the output of 'process'
        ## only if 'Verbose' is 'True'
        while bool(Verbose):
            # Read line from stdout
            output = process.stdout.readline()
            output = output.strip().decode('UTF-8')
            
            # Appending stdout to process stdout container
            STDout.append(str(output + '\n'))

            # Check if process is still running (returncode == None). 'poll()' sets and returns returncode.
            process_running = bool(process.poll() == None)
            
            # Check if process has ended or not ('process.poll() == None' means process still running)
            if  bool(output) \
            and bool(process_running):
                # Print current line in stdout
                self.UsrOut(DisplayText=(self.ShellDisplayPrefix[ExecName] + output), PSL=PrintSameLine)

            elif not bool(output) \
            and  bool(process_running):
                # If 'output' is empty but the process is still running, skip the iteration
                continue

            else:
                # If process terminated successfully (return code == 0), do not print anything
                if bool(int(process.returncode) == 0):
                    pass
                
                # Else, alert user that the process has not terminated successfully
                else:
                    self.UsrOut(DisplayText=f'PROCESS ({ExecName}) TERMINATED WITH EXIT CODE ({process.returncode})', Status='NTE', PSL=PrintSameLine, EndBreak=PrintSameLine)
                
                # Then break the while loop
                break
        
        # For 'ForceVerbose', write 'STDout' to the output file
        if  bool(Verbose) \
        and bool(ForceVerbose) \
        and bool(dumper != None):
            with open(file=__OutFile, mode='w') as out_file:
                out_file.writelines(STDout)

        # Collecting process data when process terminates
        output = process.communicate()
        outmsg = output[0].decode('UTF-8') if (output[0] != None) else ''
        errmsg = output[1].decode('UTF-8') if (output[1] != None) else ''
        excode = process.returncode

        process_data = dict({
            'OutMsg'    : outmsg,
            'ErrMsg'    : errmsg,
            'StdOut'    : STDout,
            'ExitCode'  : excode,
        })

        return process_data

    def __HandleParams(self,
        ScopeLocals:    dict    = {},
        ArgsOrder:      tuple   = (),
        Execute:        bool    = False,
        Verbose:        bool    = False,
        ForceVerbose:   bool    = False,
        PrintSameLine:  bool    = False
    ) -> dict:
        """
            ## WORKS ONLY FOR FIRST PARENT FUNCTION! DONNOT USE IT AS A GRANDCHILD!
            ### Collects target function parameters through the provided 'Locals' variable and map them to their \
            corresponding values in 'self.__CmdSet'.

            #### Args:
                - ScopeLocals (dict, optional): `locals()` of target function. Not setting it will try to catch target function `locals()`. Defaults to {}.
                - ArgsOrder (tuple, optional): Order of input/output files args and other options. Not setting it will follow parameters order. Defaults to ().
                    * Usage: `ArgsOrder = ('arg0', 'arg1', 'Options', 'arg2')` where `Options` is the rest of the arguments
                - Execute (bool, optional): Set to True to allow for command execution not only command creation as str. Defaults to False.
                - Verbose (bool, optional): Prints function progress. Defaults to False.
                - ForceVerbose (bool, optional): If True, will force display outputs usually hidden when directed to a file. e.g. `command > file`. Defaults to False.
                - PrintSameLine (bool, optional): Prints process output on the same line. Defaults to False.

            #### Returns:
                - dict: The dict includes ['Exec', 'Args', 'CmdStr', 'CmdRtrn', 'FuncName']. If ('Execute' == False), then 'CmdRtrn' will be None.
        """

        # Copying method local variables in another variable (here, 'local_vars' will contain only the parameters)
        local_vars = dict(ScopeLocals) or dict(inspect.currentframe().f_back.f_locals)
        # Get method object without calling it explicitly (inspect.stack()[1] refers to one step upper scope)
        func_name = inspect.stack()[1].function
        # Evaluate 'func_name' to get a callable method object
        func_obj = eval(f'self.{func_name}')
        # Get method params as keys and values
        params_names = inspect.signature(func_obj).parameters.keys()
        params_dict = {param: local_vars[param] for param in params_names}

        # Re-ordering 'params_dict' if required
        if bool(ArgsOrder):
            # Get arguments order from 'ArgsOrder' ignoring the 'Options' element
            args_to_order = [arg for arg in ArgsOrder if bool(arg != 'Options')]
            # Get other un-ordered arguments from 'params_names'
            other_options = [arg for arg in params_names if bool(arg not in args_to_order)]
            # 'other_options' is a list, so in order to concatenate it to string arguments
            # in 'args_to_order' we should convert args in 'args_to_order' to be '[args]'
            ordered_args = [[arg] if arg != 'Options' else arg for arg in ArgsOrder]
            # Putting options to their desired place in 'ArgsOrder'
            ordered_args[ordered_args.index('Options')] = other_options
            # Expanding list elements from lists to string
            ordered_args = [x for x in ordered_args for x in x]
            # Final step, re-order original 'params_dict'
            params_dict = {arg: params_dict[arg] for arg in ordered_args}
        else:
            pass

        # Carriers for arguments
        command_str = self.__ExcPth[func_name] + ' '
        result_args = {}

        # Looing over arguments and their values
        for param, val in params_dict.items():
            # Check if argument is Program Argument (PA) and has a value (not None)
            if  bool(param.startswith('OB_')) \
            and bool(val != None):
                # Remove program argument prefix
                param = param.replace('OB_','')

                # Check if input file exists
                if bool(param == 'InputFile'):
                    if bool(os.path.isfile(val)):
                        pass
                    else:
                        self.UsrOut(DisplayText=f'Invalid value passed to "{param}" = "{val}"! File not found!', Status='ERR')
                
                # If there is a verbose parameter, set it equal to 'Verbose' passed as an argument
                elif bool(param == 'Verbose'):
                    val = Verbose

                # Recalling the arguments values from 'self.__CmdSet'
                arg = self.__CmdSet[func_name][param](val)
                
                # Append argument to arguments dict 'result_atgs' and command string 'command_str'
                result_args[param] = arg
                command_str += arg + ' '
        
        # Execute the command if 'Execute' is enabled
        if bool(Execute):
            cmd_return = self.__ExecuteCommand(Command=command_str.strip(), ExecName='OpenBabel', Verbose=Verbose, ForceVerbose=ForceVerbose, PrintSameLine=PrintSameLine)
        else:
            cmd_return = None
        
        return dict({
            'Exec'      : self.__ExcPth[func_name],
            'Args'      : result_args,
            'CmdStr'    : command_str.strip(),
            'CmdRtrn'   : cmd_return,
            'FuncName'  : func_name,
        })

    def Obabel(self,
        OB_InputFile:           str,
        OB_OutputFile:          str,
        OB_InputFormat:         str | None      = None,
        OB_OutputFormat:        str | None      = None,
        OB_Generate2D:          bool | None     = None,
        OB_Generate3D:          bool | None     = None,
        OB_AddHydrogen:         bool | None     = None,
        OB_AddProps:            tuple | None    = None,
        OB_Center:              bool | None     = None,
        OB_ChargeCalcMethod:    str | None      = None,
        OB_DeleteHydrogens:     bool | None     = None,
        OB_JoinAllToOneFile:    bool | None     = None,
        OB_pH:                  float | None    = None,
        OB_RenameMolecule:      str | None      = None,
        OB_SaveSeparateFiles:   bool | None     = None,
        OB_SkipConversionError: bool | None     = None,
        Execute:                bool            = False,
        Verbose:                bool            = False,
        PrintSameLine:          bool            = False
    ) -> dict:
        """
            ### Interface for obabel CMD. If you don't wish to specifiy certain parameters, keep them as None.

            #### Args:
            #### All Default values are determined by the program itself.
                - OB_InputFile (str): Input molecule file path.
                - OB_OutputFile (str): Output molecule file path.
                - OB_InputFormat (str | None, optional): Specifies input format, if set to None, then will be auto-detected. Defaults to None.
                - OB_OutputFormat (str | None, optional): Specifies output format, if set to None, then will be auto-detected. Defaults to None.
                - OB_Generate2D (bool | None, optional): Generate 2D coordinates. Defaults to None.
                - OB_Generate3D (bool | None, optional): Generate 3D coordinates, ADDS HYDROGENS BY DEFAULT EVEN IF 'OB_AddHydrogen' == False. Defaults to None.
                - OB_AddHydrogen (bool | None, optional): Make all hydrogen explicit. Defaults to None.
                - OB_AddProps (tuple | None, optional): Add properties (for SDF, CML, etc.) from descriptors in list. Use -L descriptors to see available descriptors. Defaults to None.
                - OB_Center (bool | None, optional): Center atomic coordinates at (0,0,0). Defaults to None.
                - OB_ChargeCalcMethod (str | None, optional): Calculate partial charges by the specified method. List available methods using obabel -L charges. Defaults to None.
                - OB_DeleteHydrogens (bool | None, optional): Make all hydrogen implicit. Defaults to None.
                - OB_JoinAllToOneFile (bool | None, optional): Join all input molecules into a single output molecule entry. Defaults to None.
                - OB_pH (float | None, optional): Add hydrogens appropriate for pH (use transforms in phmodel.txt). Defaults to None.
                - OB_RenameMolecule (str | None, optional): Add or replace molecular title. Defaults to None.
                - OB_SaveSeparateFiles (bool | None, optional): Produce multiple output files, to allow: Splitting one input file - put each molecule into consecutively numbered output files. Batch conversion - convert each of multiple input files into a specified output format. Defaults to None.
                - OB_SkipConversionError (bool | None, optional): Continue to convert molecules after errors. Defaults to None.
                - Execute (bool, optional): Set to True to allow for command execution not only command creation as str. Defaults to False.
                - Verbose (bool, optional): Prints function progress. Defaults to False.

            #### Returns:
                - dict: The dict includes ['Exec', 'Args', 'CmdStr', 'CmdRtrn', 'FuncName']. If ('Execute' == False), then 'CmdRtrn' will be None.
        """
        # Usage: obabel [-i<input-type>] <infilename> [-o<output-type>] -O<outfilename> [Options]
        return self.__HandleParams(
            ScopeLocals=locals(),
            ArgsOrder=('OB_InputFile', 'OB_OutputFile', 'Options'),
            Execute=Execute,
            Verbose=Verbose,
            ForceVerbose=Verbose,
            PrintSameLine=PrintSameLine
        )

    def Obminimize(self,
        OB_InputFile:               str,
        OB_OutputFile:              str,
        OB_MinimizationSteps:       int,
        OB_MinimizationAlgorithm:   str | None  = None,
        OB_ForceField:              str | None  = None,
        OB_OutputFormat:            str | None  = None,
        OB_AddHydrogen:             bool | None = None,
        Execute:                    bool        = False,
        Verbose:                    bool        = False,
        PrintSameLine:              bool        = False
    ):
        """
            ### Interface for obminimize CMD. If you don't wish to specifiy certain parameters, keep them as None.

            #### Args:
            #### All Default values are determined by the program itself.
                - OB_InputFile (str): Input molecule file path.
                - OB_OutputFile (str): Output molecule file path.
                - OB_MinimizationSteps (int | None): Number of steps taken for minimization. Defaults to None.
                - OB_MinimizationAlgorithm (str | None): Minimization algorithm, either Steepest Descent (SD) or Conjugate Gradient (CG). Defaults to None.
                - OB_ForceField (str | None): Force field algorithm. Defaults to None.
                - OB_AddHydrogen (bool | None, optional): Make all hydrogen explicit. Defaults to None.
                - Execute (bool, optional): Set to True to allow for command execution not only command creation as str. Defaults to False.
                - Verbose (bool, optional): Prints function progress. Defaults to False.
                - PrintSameLine (bool, optional): Prints process output on the same line. Defaults to False.

            #### Returns:
                - dict: The dict includes ['Exec', 'Args', 'CmdStr', 'CmdRtrn', 'FuncName']. If ('Execute' == False), then 'CmdRtrn' will be None.
        """
        
        # obminimize cannot detect output format, unlike obabel.
        # so we will need to detect it manually if not provided.
        OB_OutputFormat = OB_OutputFormat if (OB_OutputFormat != None) else OB_OutputFile.split('.')[-1]

        # Usage: obminimize [options] <filename>
        # 'ForceVerbose' MUST be set to 'False' when used with 'obminimize'
        return self.__HandleParams(
            ScopeLocals=locals(), 
            ArgsOrder=('Options', 'OB_InputFile', 'OB_OutputFile'), 
            Execute=Execute, 
            Verbose=Verbose, 
            ForceVerbose=False,
            PrintSameLine=PrintSameLine
        )

    def Obconformer(self,
        OB_InputFile:           str,
        OB_OutputFile:          str,
        OB_ForceField:          str | None  = None,
        OB_NumberOfConformers:  int | None  = None,
        OB_MinimizationSteps:   int | None  = None,
        Execute:                bool        = False,
        Verbose:                bool        = False,
        PrintSameLine:          bool        = False
    ) -> dict:
        """
            ### Interface for obconformer CMD. If you don't wish to specifiy certain parameters, keep them as None.

            #### Args:
            #### All Default values are determined by the program itself.
                - OB_InputFile (str): Input molecule file path.
                - OB_OutputFile (str): Output molecule file path.
                - OB_MinimizationSteps (int | None): Number of steps taken for minimization. Defaults to None.
                - OB_NumberOfConformers (int | None): Number of conformers to generate. Defaults to None.
                - OB_ForceField (str | None): Force field algorithm. Defaults to None.
                - Execute (bool, optional): Set to True to allow for command execution not only command creation as str. Defaults to False.
                - Verbose (bool, optional): Prints function progress. Defaults to False.
                - PrintSameLine (bool, optional): Prints process output on the same line. Defaults to False.

            #### Returns:
                - dict: The dict includes ['Exec', 'Args', 'CmdStr', 'CmdRtrn', 'FuncName']. If ('Execute' == False), then 'CmdRtrn' will be None.
        """
        
        # Usage: obconformer NSteps GeomSteps <file> [forcefield]
        return self.__HandleParams(
            ScopeLocals=locals(), 
            ArgsOrder=('Options', 'OB_InputFile', 'OB_OutputFile', 'OB_ForceField'), 
            Execute=Execute, 
            Verbose=Verbose,
            ForceVerbose=False,
            PrintSameLine=PrintSameLine
        )

    def Obenergy(self,
        OB_InputFile:   str,
        OB_OutputFile:  str | None  = None,
        OB_ForceField:  str | None  = None,
        OB_AddHydrogen: bool | None = None,
        OB_Verbose:     bool | None = None,
        Execute:        bool        = False,
        Verbose:        bool        = False,
        PrintSameLine:  bool        = False
    ) -> dict:
        """
            ### Interface for obenergy CMD. If you don't wish to specifiy certain parameters, keep them as None.

            #### Args:
            #### All Default values are determined by the program itself.
                - OB_InputFile (str): Input molecule file path.
                - OB_OutputFile (str): Output molecule file path.
                - OB_ForceField (str | None): Force field algorithm. Defaults to None.
                - OB_AddHydrogen (bool | None, optional): Make all hydrogen explicit. Defaults to None.
                - OB_Verbose (bool | None): Same as 'Verbose', also copies 'Verbose' value (It is here for other code concerns). Defaults to None.
                - Execute (bool, optional): Set to True to allow for command execution not only command creation as str. Defaults to False.
                - Verbose (bool, optional): Prints function progress. Defaults to False.
                - PrintSameLine (bool, optional): Prints process output on the same line. Defaults to False.

            #### Returns:
                - dict: The dict includes ['Exec', 'Args', 'CmdStr', 'CmdRtrn', 'FuncName']. If ('Execute' == False), then 'CmdRtrn' will be None.
        """
        
        # Usage: obenergy [options] <filename>
        func_return = self.__HandleParams(
            ScopeLocals=locals(), 
            ArgsOrder=('Options', 'OB_InputFile', 'OB_OutputFile'), 
            Execute=Execute, 
            Verbose=Verbose,
            ForceVerbose=Verbose,
            PrintSameLine=PrintSameLine
        )

        # If no output file provided, then return the data to the 'OutMsg' element of 'CmdRtrn' dict
        if bool(OB_OutputFile == None):
            func_return['CmdRtrn']['MsgOut'] = [x.strip('\n') for x in func_return['CmdRtrn']['StdOut'] if x != '\n'][-1]

        return func_return

    def Obgen(self,
        OB_InputFile:       str,
        OB_OutputFile:      str,
        OB_ForceField:      str | None  = None,
        Execute:            bool        = False,
        Verbose:            bool        = False,
        PrintSameLine:      bool        = False
    ) -> dict:
        """
            ### Interface for obgen CMD. If you don't wish to specifiy certain parameters, keep them as None.

            #### Args:
            #### All Default values are determined by the program itself.
                - OB_InputFile (str): Input molecule file path.
                - OB_OutputFile (str): Output molecule file path.
                - OB_ForceField (str | None): Force field algorithm. Defaults to None.
                - Execute (bool, optional): Set to True to allow for command execution not only command creation as str. Defaults to False.
                - Verbose (bool, optional): Prints function progress. Defaults to False.
                - PrintSameLine (bool, optional): Prints process output on the same line. Defaults to False.

            #### Returns:
                - dict: The dict includes ['Exec', 'Args', 'CmdStr', 'CmdRtrn', 'FuncName']. If ('Execute' == False), then 'CmdRtrn' will be None.
        """

        # Getting user defined output file path
        usr_out_file = str(OB_OutputFile)
        # Creating temp output file path
        tmp_out_file = tempfile.NamedTemporaryFile().name
        # Re-defining user defined output file path with tmp file path
        OB_OutputFile = tmp_out_file

        # The function should now deal with the temp file in order to convert it to another type
        # Usage: obgen <filename> [options]
        # 'ForceVerbose' MUST be set to 'False' when used with 'obgen'
        func_return = self.__HandleParams(
            ScopeLocals=locals(), 
            ArgsOrder=('Options', 'OB_InputFile', 'OB_OutputFile'), 
            Execute=Execute, 
            Verbose=Verbose,
            ForceVerbose=False,
            PrintSameLine=PrintSameLine
        )
        
        # Obabel should convert standard sdf output of obgen to desired user defined output format
        # 'OB_OutputFormat' must be set to 'sdf' because this is the default out format of obgen.
        conv_return = self.Obabel(
            OB_InputFile=tmp_out_file, 
            OB_OutputFile=usr_out_file, 
            OB_InputFormat='sdf',
            Execute=Execute, 
            Verbose=Verbose,
            PrintSameLine=PrintSameLine
        )

        # Appending Obabel command to Obgen command
        func_return['CmdStr'] += ' && ' + conv_return['CmdStr']

        return func_return
