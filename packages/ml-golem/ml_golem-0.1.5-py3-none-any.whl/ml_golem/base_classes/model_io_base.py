from accelerate import Accelerator
import torch.nn as nn
from file_golem import FilePathEntries
from ml_golem.datatypes import ModelCheckpoint
from ml_golem.model_loading_logic.model_config_keywords import ModelConfigKeywords
from ml_golem.base_classes.dataloading_base import DataIterationBase
from ml_golem.base_classes.model_base import ModelBase

class ModelIOBase(DataIterationBase):
    def __init__(self, args,subconfig_keys):
        super().__init__(args,subconfig_keys)
        self.dataloader = self._initialize_dataloader(args,self.subconfig_keys)


        #TODO: REVAMP to seemlessly call for archtiecture
        architecture_info = self.data_io.fetch_config_field(
            self.global_config_name,
            subconfig_keys =[ModelConfigKeywords.ARCHITECTURE.value],
            is_required=False)
        
        if isinstance(architecture_info, str):
            self.model_identity_config_name = architecture_info
        else:
            self.model_identity_config_name = self.global_config_name

        

        self.model = self.instantiate_config_based_class(
            args,
            self.model_identity_config_name, 
            subconfig_keys =[ModelConfigKeywords.ARCHITECTURE.value])
        self.model, self.resume_epoch = self.load_model_checkpoint(self.config)
        self.is_model_wrapped_by_accelerator = False

    def _prepare_accelerator(self):
        self.accelerator = Accelerator()

        original_model_class = type(self.model)
        can_set_device = issubclass(type(self.model), ModelBase)
        original_model_type = type(self.model)
        self.model = self.accelerator.prepare(self.model)
        accelerator_model_type = type(self.model)

        self.is_model_wrapped_by_accelerator = (original_model_type != accelerator_model_type)
        if self.is_model_wrapped_by_accelerator:
            unwrapped_model = self.model.module
            if type(unwrapped_model) != original_model_class:
                raise Exception(f'Model class has been changed by the accelerator, expected: {original_model_class}, got: {type(unwrapped_model)}')

        if can_set_device:
            callable_model = self._get_callable_model()
            callable_model._set_device(self.accelerator.device)
        if hasattr(self,'dataloader'):
            self.dataloader = self.accelerator.prepare(self.dataloader)
        if hasattr(self,'optimizer'):
            self.optimizer = self.accelerator.prepare(self.optimizer)
        if hasattr(self,'loss'):
            self.loss = self.accelerator.prepare(self.loss)
        if hasattr(self,'validation_dataloader'):
            self.validation_dataloader = self.accelerator.prepare(self.validation_dataloader)
        if hasattr(self,'validation_loss'):
            self.validation_loss = self.accelerator.prepare(self.validation_loss)


    def _get_callable_model(self):
        if self.is_model_wrapped_by_accelerator:
            return self.model.module
        else:
            return self.model

    def save_model_checkpoint(self,model,epoch):
        self.data_io.save_data(ModelCheckpoint, data_args = {
            ModelCheckpoint.CONFIG_NAME: self.global_config_name,
            ModelCheckpoint.EPOCH: epoch,
            ModelCheckpoint.DATA: model.state_dict()
        })

    def load_model_checkpoint(self,task_config):
        resume_epoch =  task_config.get(ModelConfigKeywords.RESUME_EPOCH.value, -1)
        if not issubclass(type(self.model), nn.Module):
            return self.model, resume_epoch

        if resume_epoch == -1:
            data_args = {ModelCheckpoint.CONFIG_NAME: self.model_identity_config_name, #self.global_config_name,
                             ModelCheckpoint.EPOCH:FilePathEntries.OPEN_ENTRY }
            for file_path in self.data_io.get_file_iterator(ModelCheckpoint, data_args = data_args):
                missing_data_args = self.data_io.retrieve_data_args(ModelCheckpoint,data_args, file_path)
                new_epoch = int(missing_data_args[ModelCheckpoint.EPOCH])
                if new_epoch > resume_epoch:
                    resume_epoch = new_epoch

        if resume_epoch == -1:
            print('No checkpoint found, initializing model from scratch')
            resume_epoch = 0
        else:
            model_checkpoint = self.data_io.load_data(ModelCheckpoint, data_args = {
                ModelCheckpoint.CONFIG_NAME: self.model_identity_config_name, #self.global_config_name,
                ModelCheckpoint.EPOCH: resume_epoch
            })

            self.model.load_state_dict(model_checkpoint)
            self.model._set_resume_epoch(resume_epoch)
        return self.model, resume_epoch