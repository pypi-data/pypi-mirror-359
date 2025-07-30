from file_golem import FileDatatypes,AbstractDatatype,FilePathEntries
from file_golem import Config, SpecialDataArgs

class ModelCheckpoint(AbstractDatatype):
    FILE_DATATYPE = FileDatatypes.TORCH_CHECKPOINT
    EPOCH = 'epoch'
    RELATIVE_PATH_TUPLE = AbstractDatatype.RELATIVE_PATH_TUPLE + (
        'model_checkpoints',
        FilePathEntries.CONFIG_ENTRY,
        {FilePathEntries.DATA_ARG_ENTRY: EPOCH})
    


class TrainingLog(AbstractDatatype):
    FILE_DATATYPE = FileDatatypes.EMPTY
    RELATIVE_PATH_TUPLE = AbstractDatatype.RELATIVE_PATH_TUPLE + (
        'training_logs',
        FilePathEntries.CONFIG_ENTRY)



class EvaluationResults(AbstractDatatype):
    FILE_DATATYPE = FileDatatypes.JSON
    RELATIVE_PATH_TUPLE = AbstractDatatype.RELATIVE_PATH_TUPLE + (
        'evaluation_log',)


class GridShellScript(Config):
    FILE_DATATYPE = FileDatatypes.SHELL
    IS_EXECUTABLE = True  # Shell scripts are executable
    RELATIVE_PATH_TUPLE = Config.RELATIVE_PATH_TUPLE + ('_sequential_job',)


class GridSlurmScript(Config):
    FILE_DATATYPE = FileDatatypes.SLURM_SCRIPT
    IS_EXECUTABLE = True  # Slurm scripts are executable
    RELATIVE_PATH_TUPLE = Config.RELATIVE_PATH_TUPLE + ('_slurm_job',)


### SLURM OUTPUTS
class AbstractSlurmOutput(AbstractDatatype):
    SLURM_FORMAT_FILENAME = 'slurm_format_filename'
    FILE_DATATYPE = FileDatatypes.EMPTY
    RELATIVE_PATH_TUPLE = AbstractDatatype.RELATIVE_PATH_TUPLE + (
        'misc',
        'slurm',
        FilePathEntries.TIMESTAMP_CONFIG_ENTRY,)
        #'%j')
        # 
    @staticmethod
    def _retrieve_data_args(relative_path_tuple, data_args):
        config_timestamp_entry = relative_path_tuple[-1]
        timestamp = config_timestamp_entry[-data_args[SpecialDataArgs.DATA_IO]._get_timestamp_format_size():]
        data_args[AbstractSlurmOutput.TIMESTAMP_CONFIG_ENTRY_TIMESTAMP] = timestamp
        return data_args
    
    @staticmethod
    def _slurm_format_or_open_entry(data_args):
        if AbstractSlurmOutput.SLURM_FORMAT_FILENAME in data_args:
            file_name = data_args[AbstractSlurmOutput.SLURM_FORMAT_FILENAME]
            if file_name != FilePathEntries.OPEN_ENTRY:
                raise Exception('Can only use slurm format filename with open entry')
            return '*'
        else:
            return '%A_%a'
    
class SlurmOutputStd(AbstractSlurmOutput):
    FILE_DATATYPE = FileDatatypes.SLURM_OUTPUT_STD
    RELATIVE_PATH_TUPLE = AbstractSlurmOutput.RELATIVE_PATH_TUPLE + (
         {FilePathEntries.CUSTOM_LOGIC: '_slurm_format_or_open_entry'},)


class SlurmOutputErr(AbstractSlurmOutput):
    FILE_DATATYPE = FileDatatypes.SLURM_OUTPUT_ERR
    RELATIVE_PATH_TUPLE = AbstractSlurmOutput.RELATIVE_PATH_TUPLE + (
         {FilePathEntries.CUSTOM_LOGIC: '_slurm_format_or_open_entry'},)
