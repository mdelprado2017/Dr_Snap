from app.hairball3.plugin import Plugin
from app.hairball3.scriptObject import Script
import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


class DuplicateScripts(Plugin):
    """
    Plugin that analyzes duplicate scripts in scratch projects version 3.0
    """

    def __init__(self, filename, json_project, verbose=False):
        super().__init__(filename, json_project, verbose)
        self.total_duplicate = 0
        self.sprite_dict = {}
        self.duplicates = {}
        self.list_duplicate = []
        self.list_csv = []

    def get_blocks(self, dict_target):
        """
        Gets all the blocks in json format into a dictionary
        """
        out = {}


        for dict_key, dicc_value in dict_target.items():
            if dict_key == "blocks":
                print("dicc_value", dicc_value)
                if dicc_value:
                    for blocks in dicc_value:
                        print("blocks", blocks)
                        for block, blocks_value in blocks.items():
                            if block == "block":
                                print("block", blocks_value)
                                out[blocks["id"]] = blocks_value
            
        print("out", out)
        return out
    
    def set_sprite_dict(self):
        """
        Sets a dictionary containing the scripts of each sprite in Script() format
        """
        print("DUPLICATED", self.json_project.items())
        for key, list_dict_targets in self.json_project.items():
            print("KEY", key)
            print("list", list_dict_targets)
            #if key == "targets":
            #for dict_target in list_dict_targets:
               
            sprite_name = key
            sprite_blocks = self.get_blocks(list_dict_targets)
            print("sprite blocks", sprite_blocks)
            sprite_scripts = []
            
            #for key, block in sprite_blocks.items():
            #    if block == "topLevel":
            #       new_script = Script()
            #        new_script.set_script_dict(block_dict=sprite_blocks, start=key)
            #        sprite_scripts.append(new_script)
            
          
            self.sprite_dict[sprite_name] = sprite_blocks
           


    def analyze(self):
        """
        Searches for intra duplicates of each sprite and outputs them
        """
        self.set_sprite_dict()
        print("self.duplicates-------")
        print(self.sprite_dict)
        for sprite, scripts in self.sprite_dict.items():
            seen = set()
            sprite_duplicates = {}
            print(scripts)
            if not scripts:
                print(f"El sprite '{sprite}' no tiene scripts.")
                continue  # Si no hay scripts, pasa al siguiente sprite
            
            print("script",scripts)
            for script in scripts.values():
                
                
                print("script",script)
                blocks = script
                if blocks not in sprite_duplicates:
                    if len(blocks) > 5:
                        sprite_duplicates[blocks] = [(script, sprite)]
                else:
                    sprite_duplicates[blocks].append((script, sprite))
                print("hola")
                seen.add(blocks)

            print("hola",blocks)
            for key in seen:
                if key in sprite_duplicates:
                    if len(sprite_duplicates[key]) <= 1:
                        sprite_duplicates.pop(key, None)

            self.duplicates.update(sprite_duplicates)

        print("self.duplicates2-------")
        print(self.duplicates)
        
        for key, value in self.duplicates.items():
            duplicated_scripts = [pair[0] for pair in value]
            print("duplicated_Scripts")
            print(duplicated_scripts)
            print("hola")
            #csv_text = [script.get_blocks() for script in duplicated_scripts]
            #script_text = "\n\n".join([script.convert_to_text() for script in duplicated_scripts])
            print("hola")
            self.total_duplicate += sum(1 for _ in duplicated_scripts)
            #self.list_duplicate.append(script_text)
            #self.list_csv.append(csv_text)

        return self.duplicates

    def finalize(self) -> dict:

        self.analyze()

        result = ("%d duplicate scripts found" % self.total_duplicate)
        result += "\n"
        for duplicate in self.list_duplicate:
            result += str(duplicate)
            result += "\n"

        self.dict_mastery['description'] = result
        self.dict_mastery['total_duplicate_scripts'] = self.total_duplicate
        self.dict_mastery['list_duplicate_scripts'] = self.list_duplicate
        self.dict_mastery['duplicates'] = self.duplicates
       # self.dict_mastery['list_csv'] =  self.list_csv

        if self.verbose:
            logger.info(self.dict_mastery['description'])
            logger.info(self.dict_mastery['total_duplicate_scripts'])
            logger.info(self.dict_mastery['list_duplicate_scripts'])

        dict_result = {'plugin': 'duplicate_scripts', 'result': self.dict_mastery}
        print("dict_result",dict_result)
        return dict_result

