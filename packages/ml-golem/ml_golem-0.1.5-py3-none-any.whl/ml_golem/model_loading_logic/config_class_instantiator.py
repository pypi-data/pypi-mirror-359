from ml_golem.base_classes.data_io_object import DataIOObject

from ml_golem.model_loading_logic.model_config_keywords import ModelConfigKeywords

class ConfigBasedClass(DataIOObject):
    def __init__(self,args,subconfig_keys=[]):
        super().__init__(args)
        self.subconfig_keys = subconfig_keys
        self.global_config_name = args.config_name
        self.local_config_name = args.local_config_name if 'local_config_name' in args else self.global_config_name
        self.config = self.data_io.fetch_subconfig(
            self.local_config_name,
            subconfig_keys= subconfig_keys)

    def instantiate_config_based_class(self,args,config_name,subconfig_keys,default_class=None):
        config_class =self.data_io.fetch_class_from_config(
            config_name,
            subconfig_keys = subconfig_keys + [ModelConfigKeywords.MODEL_CLASS.value],
            is_required = False,)
        config_class = default_class if config_class is None else config_class
        if config_class is None:
            raise Exception(f'No class found for keys {subconfig_keys} in config {config_name}')
        
        args.local_config_name = config_name
        instantiated_class = config_class(args, subconfig_keys)
        if 'local_config_name' in args:
            del args.local_config_name
        return instantiated_class
