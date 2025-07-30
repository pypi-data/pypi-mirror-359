from itertools import product
from omegaconf import OmegaConf
from file_golem import Config, FilePathEntries
import io
import os
from enum import Enum
from ml_golem.model_loading_logic.config_class_instantiator import ConfigBasedClass
from ml_golem.datatypes import GridShellScript, GridSlurmScript, AbstractSlurmOutput, SlurmOutputStd, SlurmOutputErr
from ml_golem.model_loading_logic.model_config_keywords import ModelConfigKeywords
from ml_golem.argparse_logic.reserved_keywords import ReservedArgKeywords

class GridJobExecutionStyle(Enum):
    SEQUENTIAL = 'sequential'
    SLURM = 'slurm'
    NONE = 'none'

class GridJobBuilder(ConfigBasedClass):
    def __init__(self,args):
        super().__init__(args,subconfig_keys=[ModelConfigKeywords.GRID_JOB.value])

        self.has_grid_debug = self.config.get(ModelConfigKeywords.GRID_DEBUG.value, False)
        self.grid_actions = self.config.get(ModelConfigKeywords.GRID_ACTIONS.value)
        if len(self.grid_actions) == 0:
            raise Exception('No grid actions provided')
        self.grid_job_style = self.config.get(ModelConfigKeywords.GRID_JOB_STYLE.value)

        if self.grid_job_style == GridJobExecutionStyle.SLURM.value:
            self.slurm_config = self.data_io.fetch_subconfig(
                self.config,
                subconfig_keys=[ModelConfigKeywords.GRID_SLURM_CONFIG.value])

        grid_job_params = self.config.get(ModelConfigKeywords.GRID_JOB_PARAMS.value,[])
        self.has_grid_job_params = (len(grid_job_params) != 0)
        if self.has_grid_job_params:
            #self.grid_keys = []
            #self.grid_arrays = []

            #Should be of format [[grid_key_a, grid_key_b, ...], [grid_key_c, grid_key_d, ...], ...]
            self.all_joined_grid_job_params = {}
            grid_job_joins = self.config.get(ModelConfigKeywords.GRID_JOB_JOINS.value, [])
            join_key_set = set()
            for i in range(len(grid_job_joins)):
                join_keys = sorted(grid_job_joins[i])
                common_length = None
                for join_key in join_keys:
                    if join_key not in grid_job_params.keys():
                        raise ValueError(f'Grid job join key {join_key} not found in grid job parameters {grid_job_params.keys()}')
                    if join_key in join_key_set:
                        raise ValueError(f'Grid job join key {join_key} is duplicated in grid job joins {grid_job_joins}')
                    join_key_set.add(join_key)

                    if common_length is None:
                        common_length = len(grid_job_params[join_key])
                    elif common_length != len(grid_job_params[join_key]):
                        raise ValueError(f'Grid job join key {join_key} has a different length than the other join keys in {grid_job_joins[i]}')


                joined_params = [[self._parse_grid_job_param(grid_job_params[join_key])[j] for join_key in join_keys] for j in range(common_length)]
                self.all_joined_grid_job_params[tuple(join_keys)] = joined_params
                
            singlton_params = list(set(grid_job_params.keys() - join_key_set))
            for singleton in singlton_params:
                parsed_param = self._parse_grid_job_param(grid_job_params[singleton])
                #self.all_joined_grid_job_params[tuple([singleton])] = self._parse_grid_job_param(grid_job_params[singleton])
                self.all_joined_grid_job_params[tuple([singleton])] = [[p] for p in parsed_param]

            # print('All joined grid job parameters:', self.all_joined_grid_job_params)
            # exit()

            #for singleton in singlton_params:

                #join_keys = sorted(join_keys)

                # if not isinstance(self.grid_job_joins[i], list):
                #     raise ValueError(f'Grid job join {self.grid_job_joins[i]} is not a list. It should be a list of grid keys.')
                # if len(self.grid_job_joins[i]) == 0:
                #     raise ValueError(f'Grid job join {self.grid_job_joins[i]} is empty. It should contain at least one grid key.')

            # raw_grid_keys = []
            # raw_grid_arrays = []
            
            # for param in sorted(grid_job_params.keys()):
            #     raw_grid_keys.append(param)
            #     #self.grid_keys.append(param)

            #     unparsed_grid_job_param = grid_job_params[param]
            #     grid_job_param = self._parse_grid_job_param(unparsed_grid_job_param)
            #     raw_grid_arrays.append(grid_job_param)

                #grid_job_param = grid_job_params[param]
                # if isinstance(grid_job_param, str):
                #     if ('-' in grid_job_param) and all(part.isdigit() for part in grid_job_param.split('-')) and (len(grid_job_param.split('-')) == 2):
                #         start, end = map(int, grid_job_param.split('-'))

                #         raw_grid_arrays.append(list(range(start, end + 1)))
                #         #self.grid_arrays.append(list(range(start, end + 1)))
                #     else:
                #         raise ValueError(f"Invalid grid job parameter format: {grid_job_param}. Currently, we only support lists or ranges in the format 'start-end'.")
                # else:
                #     raw_grid_arrays.append(grid_job_param)
                    #self.grid_arrays.append(grid_job_param)


            # #check
            # for join in self.grid_job_joins:
            #     for grid_key in join:
            #         if grid_key not in raw_grid_keys:
            #             raise Exception(f'Grid job join key {grid_key} not found in grid job parameters {raw_grid_keys}')
            
            # for grid_key in raw_grid_keys:
                
            #     for join in self.grid_job_joins:
            #         for join_key in join:
            #             if 
            #             break
            #     if grid_key not in self.grid_job_joins:
            #         self.grid_job_joins.append([grid_key])
            


            self.config_list = []


    def _parse_grid_job_param(self,param):
        if isinstance(param, str):
            if ('-' in param) and all(part.isdigit() for part in param.split('-')) and (len(param.split('-')) == 2):
                start, end = map(int, param.split('-'))
                parsed_param = list(range(start, end + 1))

            else:
                raise ValueError(f"Invalid grid job parameter format: {param}. Currently, we only support lists or ranges in the format 'start-end'.")
        else:
            parsed_param = param
        return parsed_param


    def __call__(self):
        print('Building grid search...')

        self.build_configs()

        if len(self.grid_actions) == 0:
            raise Exception('No grid actions provided')
        if self.grid_job_style == GridJobExecutionStyle.SEQUENTIAL.value:
            if not self.has_grid_job_params:
                raise Exception('Grid job style is sequential, but no grid job parameters provided. Therefore it is recommended to run the action directly in the terminal instead of using the grid search builder.')
            self.build_and_execute_sequential_shell_script()
        elif self.grid_job_style == GridJobExecutionStyle.SLURM.value:
            self.build_and_execute_slurm_script()
        else:
            raise Exception(f'Grid search style {self.grid_job_style} not recognized')

    def build_and_execute_slurm_script(self):
        slurm_script_file_name, total_array_length, log_dir_name = self.build_slurm_script()

        slurm_command_buffer = io.StringIO()
        slurm_server_credentials, slurm_project_directory = self.data_io.get_slurm_server_credentials_and_project_directory()
        
        ssh_to_execute_command = (slurm_server_credentials is not None) and (slurm_project_directory is not None)
        if not ssh_to_execute_command:
            print(f'Warning: slurm server credentials or slurm project directory not provided. Will try calling slurm locally.')
        
        if ssh_to_execute_command:
            slurm_command_buffer.write(f'ssh {slurm_server_credentials} \" cd {slurm_project_directory} && ')
        
        slurm_command_buffer.write(f'sbatch ')
        if self.has_grid_job_params:
            slurm_command_buffer.write(f'-a 0-{total_array_length-1} ')
        
        slurm_command_buffer.write(f'./{slurm_script_file_name}')

        if ssh_to_execute_command:
            slurm_command_buffer.write(f' && exit \"')
        command = slurm_command_buffer.getvalue()
        slurm_command_buffer.close()
        self.data_io.run_system_command(command)
        print(f'You can check the slurm logs in the directory: {log_dir_name}')



    def build_slurm_script(self):
        script_buffer = io.StringIO()
        script_buffer.write(f'#!/bin/bash\n')
        
        partition = self.slurm_config.get('partition', 'a100')
        script_buffer.write(f'#SBATCH --partition={partition}\n')

        gpu = self.slurm_config.get('gpu', 0)
        script_buffer.write(f'#SBATCH --gres=gpu:{gpu}\n')

        cpu = self.slurm_config.get('cpu',1)
        script_buffer.write(f'#SBATCH -c {cpu}\n')

        time = self.slurm_config.get('time','01:00:00')
        script_buffer.write(f'#SBATCH -t {time}\n')

        memory = self.slurm_config.get('memory', '1G')
        script_buffer.write(f'#SBATCH --mem={memory}\n')

        data_args = {
            GridSlurmScript.CONFIG_NAME: self.global_config_name,
        }

        slurm_output_directory = self.data_io.get_data_path(SlurmOutputStd,data_args = data_args)
        self.data_io.create_directory(slurm_output_directory)
        script_buffer.write(f'#SBATCH -o {slurm_output_directory}\n')

        slurm_error_directory = self.data_io.get_data_path(SlurmOutputErr,data_args = data_args)
        script_buffer.write(f'#SBATCH -e {slurm_error_directory}\n')
        script_buffer.write(f'eval "$(conda shell.bash hook)"\n')
        script_buffer.write(f'conda activate {self.data_io.get_base_conda_name()}\n')

        if self.has_grid_job_params:
            #grid_array_lengths = [len(array) for array in self.grid_arrays]
            grid_array_lengths = [len(array) for array in self.all_joined_grid_job_params.values()]
            for i in range(len(grid_array_lengths)):
                
                modulus= grid_array_lengths[i]
                divisor = 1
                for j in range(i + 1,len(grid_array_lengths)):
                    divisor *= grid_array_lengths[j]

                script_buffer.write( f'i_{i}=$(( ($SLURM_ARRAY_TASK_ID / {divisor}) % {modulus} ))\n')

            config_file = self.data_io.get_data_path(Config, data_args={
                Config.CONFIG_NAME: self.global_config_name,
                Config.GRID_IDX: [f'${{i_{i}}}' for i in range(len(grid_array_lengths))],
            })
            self._write_command_into_script(script_buffer, config_file)

            total_array_length = 1
            for array_length in grid_array_lengths:
                total_array_length *= array_length
        else:
            config_file = self.data_io.get_data_path(Config, data_args={
                Config.CONFIG_NAME: self.global_config_name,
            })
            self._write_command_into_script(script_buffer, config_file)
            total_array_length = 1


        log_dir_name = os.path.dirname(slurm_output_directory)
        return self._save_script_and_return_path(script_buffer,GridSlurmScript) ,total_array_length, log_dir_name

    

    def config_info_iterator(self):
        #for array_combo, grid_indices in zip(product(*self.grid_arrays), product(*[range(len(array)) for array in self.grid_arrays])):
        for array_combo, grid_indices in zip(product(*self.all_joined_grid_job_params.values()), product(*[range(len(array)) for array in self.all_joined_grid_job_params.values()])):
            #grid_args = dict(zip(self.grid_keys, array_combo))
            grid_args = dict(zip(self.all_joined_grid_job_params.keys(), array_combo))
            data_args = {
                Config.CONFIG_NAME: self.global_config_name,
                Config.GRID_IDX: grid_indices}
            yield data_args, grid_args





    def build_configs(self):
        if not self.has_grid_job_params:
            return
        for config_data_args, grid_args in self.config_info_iterator():

            #print('Building config for grid args:', grid_args)
            #print('Data args:', config_data_args)
            #print(self.grid_job_joins)
            #raise Exception('stop here for now')
            override_config = OmegaConf.create({
                'defaults': [self.global_config_name],
            })
            #for grid_key in grid_args:
            print('Grid args:', grid_args)
            for config_keys, config_values in grid_args.items():

                print('Config keys:', config_keys)
                print('Config values:', config_values)
                for config_key, config_value in zip(list(config_keys), config_values):
                    print('Config key:', config_key)
                    print('Config value:', config_value)
                    #print('here', grid_args)
                    #print('here1', joined_args)
                    #key_value = joined_args[config_key]
                    if config_key == 'defaults':
                        override_config['defaults'] = [config_value] + override_config['defaults']
                    else: 
                        key_split = config_key.split('.')
                        nested_config_condition = {}
                        current = nested_config_condition
                        for key in key_split[:-1]:  
                            current = current.setdefault(key, {}) 
                        current[key_split[-1]] = config_value 

                        override_config = OmegaConf.merge(override_config, OmegaConf.create(nested_config_condition))

            config_data_args[Config.DATA]= override_config
            self.data_io.save_data(Config, data_args = config_data_args)
            config_file_name = self.data_io.get_data_path(Config, data_args = config_data_args)
            self.config_list.append(config_file_name)        

    def build_and_execute_sequential_shell_script(self):
        shell_script_file_name = self.build_shell_script()
        command = f'./{shell_script_file_name}'
        self.data_io.run_system_command(command)

    def build_shell_script(self):
        script_buffer = io.StringIO()
        script_buffer.write(f'#!/bin/bash\n')
        for config_file in self.config_list:
            self._write_command_into_script(script_buffer, config_file)
        return self._save_script_and_return_path(script_buffer,GridShellScript)
    

    def _write_command_into_script(self,script_buffer, config_file):

        for action_code in self.grid_actions:
            if (action_code == ReservedArgKeywords.INFER.value) or \
                (action_code == ReservedArgKeywords.INFER_SHORT.value) or \
                (action_code == ReservedArgKeywords.TRAIN.value) or \
                (action_code == ReservedArgKeywords.TRAIN_SHORT.value):
                script_buffer.write('accelerate launch')
                if self.grid_job_style == GridJobExecutionStyle.SLURM.value:
                    gpu = self.slurm_config.get('gpu', 0)
                    if gpu > 1:
                        script_buffer.write(' --multi_gpu')
                        print('WARNING: Using multi_gpu mode with SLURM, you will likely encounter port in use errors.')
                        print('Support for this is not implemented yet.')
                        print('A partial solution is to use the  --main_process_port to specify a port that is not in use.')
                        print('However, dev is still on going')
            else:
                script_buffer.write('python')

            script_buffer.write(f' main.py --{action_code} -c {config_file}')
            if self.has_grid_debug:
                script_buffer.write(f' --{ReservedArgKeywords.DEBUG.value}')
            script_buffer.write('\n')
            script_buffer.write(f'echo ""\n')
    
    def _save_script_and_return_path(self,script_buffer,script_class):
        script = script_buffer.getvalue()
        script_buffer.close()
        data_args = {
            script_class.CONFIG_NAME: self.global_config_name,
            script_class.DATA: script}
        
        self.data_io.save_data(script_class, data_args = data_args)
        script_file_name = self.data_io.get_data_path(script_class, data_args = data_args)
        return script_file_name


class GridJobViewer(GridJobBuilder):
    def __init__(self,args):
        super().__init__(args)

    def __call__(self):
        if self.grid_job_style != GridJobExecutionStyle.SLURM.value:
            raise Exception(f'Grid job viewer can only be used with SLURM style grid jobs, but got {self.grid_job_style}')

        latest_directory = None
        latest_timestamp = None
        for slurm_output_directory, data_args in self.data_io.get_file_iterator(AbstractSlurmOutput,
            data_args = {
                AbstractSlurmOutput.CONFIG_NAME: self.global_config_name,
                AbstractSlurmOutput.TIMESTAMP_CONFIG_ENTRY_TIMESTAMP: FilePathEntries.OPEN_ENTRY},
            can_return_data_args= True,
            ):
            latest_directory = slurm_output_directory
            latest_timestamp = data_args[AbstractSlurmOutput.TIMESTAMP_CONFIG_ENTRY_TIMESTAMP]

        if latest_directory is None:
            raise Exception(f'No SLURM output directory found for config {self.global_config_name}. Please run the grid job first.')
        
        print(f'Latest SLURM job directory: {latest_directory}')

        print('All output files for the latest SLURM job:')
        for slurm_output in self.data_io.get_file_iterator(SlurmOutputStd, data_args = {
            SlurmOutputStd.CONFIG_NAME: self.global_config_name,
            SlurmOutputStd.TIMESTAMP_CONFIG_ENTRY_TIMESTAMP: latest_timestamp,
            SlurmOutputStd.SLURM_FORMAT_FILENAME: FilePathEntries.OPEN_ENTRY}):
            print(slurm_output)

        print('All error files for the latest SLURM job:')
        for slurm_error in self.data_io.get_file_iterator(SlurmOutputErr, data_args = {
            SlurmOutputErr.CONFIG_NAME: self.global_config_name,
            SlurmOutputErr.TIMESTAMP_CONFIG_ENTRY_TIMESTAMP: latest_timestamp,
            SlurmOutputErr.SLURM_FORMAT_FILENAME: FilePathEntries.OPEN_ENTRY}):
            print(slurm_error)
        

        

        # print('Grid search configurations:')
        # for config_file in self.config_list:
        #     print(config_file)
        # print('Grid search complete.')