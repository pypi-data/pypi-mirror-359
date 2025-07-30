from ml_golem.base_classes.model_io_base import ModelIOBase
import torch.nn as nn
class ModelInference(ModelIOBase):
    def __init__(self,args,subconfig_keys):
        super().__init__(args,subconfig_keys)

        if isinstance(self.model, nn.Module):
            self._prepare_accelerator()

    def __call__(self):

        callable_model = self._get_callable_model()
        if self.dataloader is None:
            results = self.make_inference(self.model)
            self.save_inference_results(results,callable_model)
        else:
            for input_data in self.dataloader:
                results = self.make_inference(self.model,input_data)
                self.save_inference_results(results,callable_model,input_data)

        self.complete_inference()


    def make_inference(self,model,input_data=None):
        if input_data is None:
            output = model()
        else:
            output = model(input_data)
        return output
    
    def save_inference_results(self,output,model,input_data=None):
        if hasattr(model, 'save_results'):
            model.save_results(output, input_data)


    def complete_inference(self):
        if hasattr(self.model, 'complete_inference'):
            self.model.complete_inference()
