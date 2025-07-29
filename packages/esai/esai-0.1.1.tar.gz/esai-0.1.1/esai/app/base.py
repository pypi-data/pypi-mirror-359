import os
import yaml

from ..pipeline import PipelineFactory

class Application:
    @staticmethod
    def read(data):     #data should be file path ("file.yaml") or string ("{'path':{'filepath'}}") or dict ({"path":"file"})
        if isinstance(data, str):
            if os.path.exists(data):
                with open(data, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
                
            data = yaml.safe_load(data)
            if not isinstance(data, str):
                return data
                
            raise FileNotFoundError(f"Unable to load file '{data}'")
        return data    
    
    def __init__(self, config):
        self.config = Application.read(config)

        self.createpipelines()

    def createpipelines(self):
        self.pipelines = {}

        pipelines = list(PipelineFactory.list().keys())                                 #listing all short names ("textractor")

        for key in self.config:                                                         #listing custom pipeline names ("esai.pipeline.data.textractor.Textractor")
            if "." in key:
                pipelines.append(key)                                                   #listing all names

        for pipeline in pipelines:                                                      #parameters storing
            if pipeline in self.config:
                config = self.config[pipeline] if self.config[pipeline] else {}

                self.pipelines[pipeline] = PipelineFactory.create(config, pipeline) 
