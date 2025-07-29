import logging
import app.consts_drscratch as consts
from app.hairball3.plugin import Plugin
from app.hairball3.scriptObject import Script
logger = logging.getLogger(__name__)


class DeadCode(Plugin):
    """
    Plugin that indicates unreachable code in Scratch files
    """

    def __init__(self, filename, json_project):
        super().__init__(filename, json_project)
        self.dead_code_instances = 0
        self.dict_deadcode = {}
        self.opcode_argument_reporter = "argument_reporter"

    def get_blocks(self, dict_target):
        """
        Gets all the blocks in json format into a dictionary
        """
        out = {}


        for dict_key, dicc_value in dict_target.items():
            if dict_key == "blocks":
                for blocks, blocks_value in dicc_value.items():
                    if type(blocks_value) is dict:
                        out[blocks] = blocks_value
        
        return out

    def analyze(self):

        sprites = {}
        #print("prueba",self.json_project.items())
        for key, value in self.json_project.items():
            blocks_list = []
            if "blocks" in value:
                #print("valor", value)
                
                
               
                for blocks_dicc in value["blocks"]:
                    #print(blocks_dicc)
                    sprite = key
                    if type(blocks_dicc) is dict:
                        block_name = blocks_dicc["block"]
                        next_blocks = blocks_dicc.get("next", [])
                        #print("entras")
                        event_var = any(blocks_dicc["block"] == event for event in consts.PLUGIN_DEADCODE_LIST_EVENT_VARS)
                        loop_block = any(blocks_dicc["block"] == loop for loop in consts.PLUGIN_DEADCODE_LIST_LOOP_BLOCKS)

                        if event_var or loop_block:
                            #print("entras2")
                            if not self.opcode_argument_reporter in blocks_dicc["block"]:
                                
                                #print("entras3")
                                if not next_blocks:
                                    #print("entras4.2")
                                    #print(blocks_dicc)
                                    script = Script()
                                    block = script.convert_block_to_text(blocks_dicc)
                                    blocks_list.append(str(block))
                                    #blocks_list.append(str(blocks_dicc.get("block")))
                                
                                    # Check dead loop blocks
                                    #print(loop_block)
                                    #print(blocks_dicc)                 
                                

            if blocks_list:
                scripts = []
                for block in blocks_list:
                    print( "bloque", block)
                    sprites[sprite] = blocks_list
                    self.dead_code_instances += 1

        self.dict_deadcode = sprites

    def finalize(self):

        self.analyze()

        result = "{}".format(self.filename)

        if self.dead_code_instances > 0:
            result += "\n"
            result += str(self.dict_deadcode)

        self.dict_mastery['description'] = result
        self.dict_mastery['total_dead_code_scripts'] = self.dead_code_instances
        self.dict_mastery['list_dead_code_scripts'] = [self.dict_deadcode]

        dict_result = {'plugin': 'dead_code', 'result': self.dict_mastery}
        print("dict_result_dead",dict_result)
        return dict_result



