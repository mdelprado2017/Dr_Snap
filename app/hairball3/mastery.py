import json
from app.hairball3.plugin import Plugin
import app.consts_drscratch as consts
import logging
import coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)


class Mastery(Plugin):

    def __init__(self, filename: str, json_project, skill_points: dict, mode: str ,verbose=False):
        super().__init__(filename, json_project, skill_points, mode , verbose)
        self.possible_scores = {"advanced": 4, "proficient": 3, "developing": 2, "basic": 1} # Falta añadir Finesse
        self.dict_total_blocks = {}
        self.total_blocks = 0

    def process(self):

        for key, list_info in self.json_project.items():
            #print("contraseña", key)
            #print("contraseña", list_info)

            for dicc_key, dicc_value in list_info.items():
               
                if dicc_key == "blocks":
                    #print("dicc_value", dicc_value)
                    for block_dicti in dicc_value:
                        #print(block_dicti)
                        if type(block_dicti) is dict:
                            self.list_total_blocks.append(block_dicti)
                            self.dict_total_blocks[block_dicti['block']] = block_dicti
        
        #print("total", list_total_blocks)
        for block in self.list_total_blocks:
            for key, list_info in block.items():
                if key == "block":
                    self.dict_blocks[list_info] += 1
                    self.total_blocks += 1
        #print("noseeeee", self.dict_blocks)
        #print("noseeeee", self.list_total_blocks)


    def analyze(self):
        self.compute_logic()
        self.compute_flow_control()
        self.compute_synchronization()
        self.compute_abstraction()
        self.compute_data_representation()
        self.compute_user_interactivity()
        self.compute_parallelization()
        self.compute_math_operators()
        self.compute_motion_operators()


    
    def finalize(self) -> dict:

        self.process()
        self.analyze()

        # print("Dict:", self.dict_total_blocks)

        total_points = 0
        active_dimensions = sum(1 for value in self.skill_points.values() if value > 0)

        for skill, skill_grade in self.dict_mastery.items():
            if self.verbose:
                logger.info('Skill: {}, points: {}'.format(skill, skill_grade))
            total_points = total_points + skill_grade[0]
            total_points = round(total_points, 2)

        try:
            average_points = float(total_points) / active_dimensions
        except ZeroDivisionError:
            average_points = 0

        total_maxi_points = sum(self.skill_points.values())
        competence = self.set_competence(total_points, total_maxi_points)

        result = '{}{}{}{}'.format(self.filename, '\n', json.dumps(self.dict_mastery), '\n')
        result += ('Total mastery points: {}/{}\n'.format(total_points, total_maxi_points))
        result += ('Average mastery points: {}/{}\n'.format(average_points, consts.PLUGIN_MASTERY_AVG_POINTS))

        self.set_dict(self.dict_mastery, total_points, total_maxi_points, average_points, competence)

        if self.mode == 'Personalized':
            dict_result = {'plugin': 'mastery', 'personalized': self.dict_mastery}
        elif self.mode == 'Default' or self.mode == 'Comparison' or self.mode == 'Recommender':
            vanilla_dict = self.calc_extrapolation(self.dict_mastery)
            vanilla_points = sum(points[0] for points in vanilla_dict.values())
            average_points = vanilla_points / 7
            vanilla_competence = self.set_competence(vanilla_points, 21, 'Vanilla')
            self.set_dict(vanilla_dict, vanilla_points, 21, average_points, vanilla_competence)
            #self.dict_mastery['description'] = result
            if self.verbose:
                logger.info(self.dict_mastery['description'])
            dict_result = {'plugin': 'mastery', 'extended': self.dict_mastery, 'vanilla': vanilla_dict}

        print("DICT_RESULT: ", dict_result)

        return dict_result

    def set_dict(self, dict, points, max_points, average_points, competence) -> dict:
        """
        Include the mastery points, max points, average points and competence in the dictionary.
        """
        dict['total_points'] = [points, max_points]
        dict['total_blocks'] = self.total_blocks
        dict['max_points'] = max_points
        dict['average_points'] = round(average_points, 2)
        dict['competence'] = competence

        return dict

    def calc_extrapolation(self, dict_mastery) -> dict:
        """
        Extrapolate the points of the extended mode to the vanilla mode.
        """
        mastery = {'Logic', 'FlowControl', 'Synchronization', 'Abstraction', 'DataRepresentation', 
                'UserInteractivity', 'Parallelization'}
        
        new_dict = {}
        for skill in dict_mastery:
            if skill in mastery:
                if dict_mastery[skill][0] > 3:
                    new_value = 3
                else:
                    new_value = dict_mastery[skill][0]
                new_dict[skill] = [new_value, 3]
        return new_dict
    
    def set_competence(self, points, max_points, mode=None):

        competence = ''

        # finesse_lvl = max_points*36/45
        advanced_lvl = max_points*27/45
        proficient_lvl = max_points*18/45
        developing_lvl = max_points*9/45

        if mode == 'Vanilla':
            if points > 15:
                # result = "Overall programming competence: Proficiency"
                competence = 'Master'
            elif points > 7:
                # result = "Overall programming competence: Developing"
                competence = 'Developing'
            else:
                # result = "Overall programming competence: Basic"
                competence = 'Basic'
        else:
            #if points > finesse_lvl: --> FALTA POR AÑADIR
                # result = "Overall programming competence: Finesse"
                # competence = 'Finesse'
            if points > advanced_lvl:
                # result = "Overall programming competence: Advanced"
                competence = 'Advanced'
            elif points > proficient_lvl:
                # result = "Overall programming competence: Proficiency"
                competence = 'Master'
            elif points > developing_lvl:
                # result = "Overall programming competence: Developing"
                competence = 'Developing'
            else:
                # result = "Overall programming competence: Basic"
                competence = 'Basic'
        """
        competence_dict = {
            'result': result, 
            'programming_competence': competence
            }       
        """

        return competence
    
    def set_dimension_score(self, scale_dict, dimension):

        score = 0
        print("Scale", scale_dict)
        for key, value in scale_dict.items():
            if type(value) == bool and value is True:
                if key in self.possible_scores.keys():
                    print(dimension + " : " + key)
                    score = self.extrapolate_to_rubric(dimension, key)
                    self.dict_mastery[dimension] = [score, self.skill_points[dimension]] 
                    return
        print(dimension + " : " + "None")
        self.dict_mastery[dimension] = [score, self.skill_points[dimension]] 
        return

    def extrapolate_to_rubric(self, dimension, level):
        """
        Extrapolate the points to the max points of skill rubric
        """
        if self.possible_scores[level] >= self.skill_points[dimension]:
            score = self.skill_points[dimension]
        else:
            score = self.possible_scores[level]
        return score

    def compute_logic(self):
        """
        Assign the logic skill result
        """

        basic = self.check_list({'doIf'})
        developing = self.check_list({'doIfElse','reportIfElse'})
        print("devreeeeeeeeeeeeeeeeeeeeeeeeeeeeeee", developing)

        proficient = self.check_list({'reportAnd','reportVariadicAnd' 'reportOr','reportVariadicOr', 'reportNot'})
        advanced = self.check_nested_conditionals()
        # finesse = PREGUNTAR GREGORIO
        print("mastereeeeeeeeeeeeeeeeeeeeeeeeeeeeeee", proficient)
        scale_dict = {"advanced": advanced, "proficient": proficient, "developing": developing, "basic": basic}

        self.set_dimension_score(scale_dict, "Logic")
        

    def compute_flow_control(self):
        """
        Calculate the flow control score
        """

        basic = self.check_block_sequence()
        developing = self.check_list({'doRepeat', 'doForever'})
        proficient = self.check_list({'doUntil', 'for'})
        advanced = self.check_nested_loops()

        # finesse = PREGUNTAR GREGORIO

        scale_dict = {"advanced": advanced, "proficient": proficient, "developing": developing, "basic": basic}

        self.set_dimension_score(scale_dict, "FlowControl")
        

    def compute_synchronization(self):
        """
        Compute the syncronization score
        """

        basic = self.check_list({'doWait'})
        developing = self.check_list({'doBroadcast', 'receiveMessage', 'doStopThis', 'doPauseAll'})
        proficient = self.check_list({'doWaitUntil', 'doBroadcastAndWait', 'receiveOnClone', 'receiveCondition'})
        advanced = self.check_dynamic_msg_handling()
        # finesse = PREGUNTAR GREGORIO

        scale_dict = {"advanced": advanced, "proficient": proficient, "developing": developing, "basic": basic}

        self.set_dimension_score(scale_dict, "Synchronization")


    def compute_abstraction(self):
        """
        Compute the abstraction score
        """

        basic = self.check_more_than_one()
        developing = self.check_list({'receiveOnClone'})
        proficient = self.check_list({'procedures_definition'})
        advanced = self.check_advanced_clones()
        print("ADVANCED CLONES:", advanced)
        # finesse = PREGUNTAR GREGORIO

        scale_dict = {"advanced": advanced, "proficient": proficient, "developing": developing, "basic": basic}

        self.set_dimension_score(scale_dict, "Abstraction")


    def compute_data_representation(self):
        """
        Compute data representation skill score
        """

        modifiers = self.check_list({
            'forward', 'gotoXY', 'doGlide', 'setXPosition', 'setYPosition',
            'changeXPosition', 'changeYPosition', 'setHeading', 'doFaceTowards',
            'turn', 'turnLeft', 'doGotoObject', 'changeScale', 'setScale',
            'doSwitchToCostume', 'doWearNextCostume', 'changeEffect', 'setEffect',
            'show', 'hide'
        })

        lists = self.check_list({
            'reportListAttribute',  'doInsertInList', 'doDeleteFromList', 'doAddToList',
            'doReplaceInList', 'reportListContainsItem'
        })
        
        boolean_logic = self.check_list({
            'reportVariadicEquals', 'reportVariadicLessThan', 'reportVariadicAnd', 'reportVariadicOr', 'reportNot', 'reportVariadicGreaterThan',
        })
        
        variables = self.check_list({'doChangeVar', 'doSetVar'})
        
        scale_dict = {"advanced": boolean_logic, "proficient": lists, "developing": variables, "basic": modifiers}
        
        self.set_dimension_score(scale_dict, "DataRepresentation")


    def compute_user_interactivity(self):
        """Assign the User Interactivity skill result"""

        # ----------- ADVANCED ------------------------
        advanced = self.check_ui_advanced()

        # ----------- PROFIENCY --------------
        proficient = self.check_ui_proficiency()

        # ---------- DEVELOPING ------------------------
        developing = self.check_ui_developing()

        # ----------- BASIC -------------------------------------
        basic = self.check_list({'receiveGo', 'receiveKey'})

        scale_dict = {"advanced": advanced, "proficient": proficient, "developing": developing, "basic": basic}
        self.set_dimension_score(scale_dict, "UserInteractivity")
    
    def check_ui_advanced(self):
        """
        Check the advanced user interactivity skills
        """
        non_controllers_ext = ['music', 'pen', 'videoSensing', 'text2speech', 'translate']

        extensions = self.json_project.get('extensions', [])
        print("---EXTENSIONS---")
        print(extensions)
        print("----------------")

        return any(extension not in non_controllers_ext for extension in extensions)

        
    def compute_parallelization(self):
        """
        Assign the Parallelism skill result
        """
        print("fin, principio")

        dict_parall = self.parallelization_dict()
        print("fiio")
        # ---------- ADVANCED ----------------------------
        advanced = self.check_p_advanced(dict_parall)
        print("fin")
        # ---------- PROFICIENT ----------------------------
        proficient = self.check_p_proficiency(dict_parall)
        print("fya")
        # ---------- DEVELOPING ----------------------------     
        developing = self.check_p_developing(dict_parall)
        print("f")
        # ----------- BASIC ----------------------------
        basic = self.check_scripts_flag(n_scripts=2)
        print("fin, principio")
        scale_dict = {"advanced": advanced, "proficient": proficient, "developing": developing, "basic": basic}
        print("final")

        self.set_dimension_score(scale_dict, "Parallelization")
    
    def parallelization_dict(self):
        dict_parallelization = {}
        
        print(self.list_total_blocks)
        for block in self.list_total_blocks:
            for key, value in block.items():
                
                # Asegurar que las claves existen antes de hacer append
                if key == 'option':  
                    if 'BROADCAST_OPTION' not in dict_parallelization:
                        dict_parallelization['BROADCAST_OPTION'] = []  # Inicializar como lista vacía
                    dict_parallelization['BROADCAST_OPTION'].append(value)
        print("---------------------------------------------")
        for key, list_info in self.json_project.items():
        #print("contraseña", key)
        #print("contraseña", list_info)
            for dicc_key, dicc_value in list_info.items():
                
                if dicc_key == "costumes":
                        if 'BACKDROP' not in dict_parallelization:
                            dict_parallelization['BACKDROP'] = []  # Inicializar como lista vacía
                        # Si dicc_value es una lista, añadimos cada valor de esa lista a dict_parallelization['BACKDROP']
                        if isinstance(dicc_value, list):
                            dict_parallelization['BACKDROP'].extend(dicc_value)  # extend agrega los elementos de dicc_value a BACKDROP
                        else:
                            dict_parallelization['BACKDROP'].append(dicc_value)  
                                
        
        print("noseee",dict_parallelization)
        return dict_parallelization
        
        
    def compute_math_operators(self):
        """
        Assign the Use of Math Operators skill result
        """
        basic = self.check_list({'reportVariadicSum', 'reportDifference', 'reportVariadicProduct', 'reportQuotient'})
        developing = self.check_formula()
        proficient = self.check_list({'reportJoinWords', 'reportLetter', 'reportTextAttribute'})
        advanced = self.check_trigonometry()

        scale_dict = {"advanced": advanced, "proficient": proficient, "developing": developing, "basic": basic}
        self.set_dimension_score(scale_dict, "MathOperators")

    def compute_motion_operators(self):
        """
        Assign the Use of Motion Operators skill result
        """

        basic = self.check_list({'forward', 'gotoXY', 'changeXPosition', 'doGotoObject', 'changeYPosition', 'setXPosition', 'setYPosition'})
        developing = self.check_list({'turnLeft', 'turn', 'setHeading', 'doFaceTowards'})
        proficient = self.check_list({'doGlide', 'changeXPosition','changeYPosition'})
        print("-----------------adddddddddddddddd")
        advanced = self.check_motion_complex_sequences()
        # finesse = PREGUNTAR GREGORIO

        scale_dict = {"advanced": advanced, "proficient": proficient, "developing": developing, "basic": basic}

        self.set_dimension_score(scale_dict, "MotionOperators") 


    def check_formula(self):
        """
        Checks if the script contains a base operator with 3 or more nested operators within its inputs.
        """

        operators = ['reportVariadicSum', 'reportDifference', 'reportVariadicProduct',
                    'reportQuotient', 'operator_mathop', 'operator_random']


        # Iterate over all blocks to find base operators
        for block in self.list_total_blocks:
            if block['block'] in operators:
                # Count the nested operators within this base operator
                counter = self.count_nested_operators(block, operators)
                print(f"Nested operators for block {block['block']}: {counter}")
                
                # If we find 1 or more nested operators, return True
                if counter >= 1:
                    return True
        return False

    def count_nested_operators(self, block, operators):
        """
        Recursively counts the number of nested operators within a block, not counting the initial block.
        """
        
        count = 0 
        for b, value in block.items():
            if( b == "block"):
                # Check if there is a string representing a block ID
                block_ids = [v for v in value if isinstance(v, str) and v in self.dict_total_blocks]
               

                for connected_block_id in block_ids:
                    connected_block = self.dict_total_blocks[connected_block_id]
                    
                    # If the connected block is an operator, count that operator and keep searching
                    if connected_block['block'] in operators:

                        count += 1
                        # Recursively count operators within this operator
                        count += self.count_nested_operators(connected_block, operators)
            
        return count

    def check_scripts_flag(self, n_scripts):
        if self.dict_blocks['receiveGo'] >= n_scripts:  # N Scripts on green flag
            return True
        return False

    def check_scripts_key(self, dict_parall, n_scripts):
        if self.dict_blocks['receiveMessage'] >= n_scripts:  # N Scripts start on the same key pressed
            return True
           

        return False
    
    def check_scripts_sprite(self, n_scripts):
        if self.dict_blocks['event_whenthisspriteclicked'] >= n_scripts:  # Sprite with N scripts on clicked
            return True
        return False

    def check_list(self, list):

        for item in list:
            if item in self.dict_blocks.keys():
                return True
            
        return False
    
    def check_scripts(self, n_scripts):
        coincidences = 0
        for block in self.dict_total_blocks.values(): 
            #deberia de ser con next
            if block['block'] == 'doif':
                condition = block['next']
                if (condition != None):
                    for hijo in self.dict_total_blocks.values():
                        if hijo['id'] == condition:
                           
                            if hijo['block'] == 'operator_greaterThan' or hijo['block'] == 'reportVariadicGreaterThan':
                                coincidences += 1
                                if coincidences >= n_scripts: # N scripts when %s is > %s,
                                    print("check_scripts t")
                                    return True
        print("check_scripts f")
        return False

    def check_scripts_media(self, dict_parall, n_scripts):
        print("PARALL", dict_parall)
        if self.dict_blocks['whenGreaterThan'] >= n_scripts:  # N Scripts start on the same multimedia (audio, timer) event
            if dict_parall['WHENGREATERTHANMENU']:
                var_list = set(dict_parall['WHENGREATERTHANMENU'])
                for var in var_list:
                    if dict_parall['WHENGREATERTHANMENU'].count(var) >= n_scripts:
                        print("check_scripts_media t")
                        return True
        print("check_scripts_media f")
        return False
    
    def check_scripts_backdrop(self, dict_parall, n_scripts):
        if dict_parall['BACKDROP']:
            backdrop_list = set(dict_parall['BACKDROP'])
            for var in backdrop_list:
                if dict_parall['BACKDROP'].count(var) >= n_scripts:
                    print("check_scripts_backdrop t")

                    return True
        print("check_scripts_backdrop f")
        return False
    
    def check_scripts_msg(self, dict_parall, n_scripts):
        try:
            print("check_scripts_msg 1")
            if self.dict_blocks['receiveMessage'] >= n_scripts:  # N Scripts start on the same received message
                print("check_scripts_msg 2")
                if dict_parall['BROADCAST_OPTION']:
                    print("check_scripts_msg 3")
                    var_list = set(dict_parall['BROADCAST_OPTION'])
                    for var in var_list:
                        print(dict_parall['BROADCAST_OPTION'].count(var))
                        print(n_scripts)
                        if dict_parall['BROADCAST_OPTION'].count(var) >= n_scripts:
                            return True
            print("check_scripts_msg f")
            return False
        except Exception as e:
            print(f"Error in check_scripts_msg: {e}")
    
    def check_scripts_video(self, n_scripts):
        if self.dict_blocks['videoSensing_motionGreaterThan'] >= n_scripts:  # N Scripts start on the same multimedia (video) event
            return True        
        print("check_scripts_video f")
        return False
    
    def check_ui_proficiency(self):
        """
        Check if the user has proficient user interactivity
        """
        proficiency = {'videoSensing_motionGreaterThan', 'reportVideo', 'doSetVideoTransparency',
                       'reportAudio', 'reportTouchingColor'}
        
        if self.check_list(proficiency) or self.check_scripts(n_scripts=2):
            return True

        return False
    
    def check_mouse_blocks(self):
        if self.dict_blocks['motion_goto_menu'] or self.dict_blocks['sensing_touchingobjectmenu']:
            if self._check_mouse() == 1:
                return True
        return False
        
    def check_ui_developing(self):
        """
        Check if the user has developing user interactivity
        """
        developing = {'receiveKey',  'reportMouseDown', 'reportKeyPressed',
                      'doAsk', 'getLastAnswer'}

        if self.check_list(developing) or self.check_mouse_blocks():
            return True
        
        return False
    
        
    def check_p_advanced(self, dict_parall):
        """
        Check the advanced parallelization skills
        """
        print("llego ADVANCED")
        if (self.check_scripts(n_scripts=3) or self.check_scripts_media(dict_parall, n_scripts=3) or self.check_scripts_backdrop(dict_parall, n_scripts=3) 
            or self.check_scripts_msg(dict_parall, n_scripts=3) or self.check_scripts_video(n_scripts=3)):
            print("t")
            return True
        print("f")
        return False
        
    
    def check_p_proficiency(self, dict_parall):
        if (self.check_scripts(n_scripts=2) or self.check_scripts_media(dict_parall, n_scripts=2) or self.check_scripts_backdrop(dict_parall, n_scripts=2) 
            or self.check_list({'createClone'}) or self.check_scripts_msg(dict_parall, n_scripts=2) or self.check_scripts_video(n_scripts=2)):
            return True
        return False
    
    def check_p_developing(self, dict_parall):
        if self.check_scripts_key(dict_parall, n_scripts=2) or self.check_scripts_sprite(n_scripts=2):
            return True
        return False
    
    def check_more_than_one(self):
        
        check = False

        count = 0
        for block in self.list_total_blocks:
            block_id = str(block.get("id", ""))  # Convertimos el id a string para analizarlo
        
            # Verificamos que el id es un número entero (sin ".") y que no tenga "next"
            if block_id.isdigit() and "next" not in block:
                count += 1
        if count > 1:
            check = True

        return check
    
    def check_advanced_clones(self):

        check = False
        #print("check_advanced_clones")
        for block in self.list_total_blocks:
            if block['block'] == "receiveOnClone":

                next = block['id']
                
                current_id = str(next)  # Convertimos msg en cadena para evitar errores
                if '.' in current_id:
                    current_parts = current_id.split('.')  # Dividimos el ID por puntos (ej. '1.1' -> ['1', '1'])
                    # Vamos a buscar los siguientes bloques incrementando la última parte del ID
                    next_part = int(current_parts[-1]) + 1  # Incrementamos la última parte
                    current_parts[-1] = str(next_part)  # Reemplazamos la última parte con el nuevo valor
                    # Ahora construimos el siguiente ID
                    parent_id = '.'.join(current_parts)  # Convertimos la lista de nuevo en un ID
                else:
                    parent_id = str(int(current_id) + 1)

                if self.check_broadcast(parent_id) or self.check_loops(parent_id) or self.check_conditional(parent_id):
                    check = True
                    return check

        return check
    
    def check_broadcast(self, parent_id):

        check = False

        list = {'doBroadcast', 'doBroadcastAndWait'}
        for substack in self.list_total_blocks:
            if str(substack['id']) == parent_id:
                parent_block = substack['block']  # Asignamos el bloque padre
                # Si encontramos el bloque
                #print(f"Bloque encontrado: {parent_block} con ID: {parent_id}")

                break

        if parent_block in list:
            check = True
        #print("no fallo")
        return check
    
    def check_loops(self, parent_id):

        loops = {'doForever', 'doRepeat', 'doUntil'}


        check = False
        for substack in self.list_total_blocks:
           
            if str(substack['id']) == str(parent_id):
                parent_block = substack['block']  # Asignamos el bloque padre
                # Si encontramos el bloque
                #print(f"Bloque encontrado LOOPS: {parent_block} con ID: {parent_id}")

                break
       
        for loop in loops:
            if loop == parent_block:   
                    check = True
            
        return check

        


    
    def check_conditional(self, parent_id):

        check = False
        for substack in self.list_total_blocks:  

            if str(substack['id']) == str(parent_id):
                parent_block = substack['block']  # Asignamos el bloque padre
                # Si encontramos el bloque
                #print(f"Bloque encontrado CONDICIONAL: {parent_block} con ID: {parent_id}")

                break
       
    
        if parent_block == 'doIf':
                check = True
           
        elif parent_block == 'doIfElse':
                check = True
            

        return check

    def _check_mouse(self):
        """
        Check whether there is a block 'go to mouse' or 'touching mouse-pointer?
        """

        for block in self.list_total_blocks:
            for key, value in block.items():
                if key == 'fields':
                    for mouse_key, mouse_val in value.items():
                        if (mouse_key == 'TO' or mouse_key == 'TOUCHINGOBJECTMENU') and mouse_val[0] == '_mouse_':
                            return 1

        return 0

    def check_trigonometry(self):

        check = False

        list = {'cos', 'sin', 'tan', 'asin', 'acos', 'atan', 'atan2'}

        for block in self.list_total_blocks:
            if(block['block'] == 'reportMonadic'):
                if block['option'] in list:
                    check = True
                    return check
                
        return check

    
    def check_motion_complex_sequences(self):

        check = False
        min_motion_blocks = 5
        counter = 0
        list = {'forward', 'gotoXY', 'doGlide',
                'setXPosition', 'setYPosition', 'changeXPosition', 'changeYPosition', 
                'setHeading', 'doFaceTowards', 'turn', 'turnLeft', 
                'doGotoObject', 'bounceOffEdge'}
                           
        
       
        for item in list:
            for block in self.list_total_blocks:
                
            
                if block['block'] == item:
                    counter += 1
                    #print(counter)
                    if counter >= min_motion_blocks:
                        check = True
                        return check


        return check
    
    
    def check_dynamic_msg_handling(self):

        check = False
        counter = 0
        min_msg = 3

        for block in self.list_total_blocks:
            if block.get('block') == "doBroadcast" or block.get('block') == "doBroadcastAndWait" :
                try:
                    #("-------------dynamic---------------")
                    #print(block['block'])
                    msg = block['id']
                    #print(msg)
                   
                    if self.has_conditional_or_loop(msg):
                        counter += 1
                        #print("Counter", counter)
                except IndexError:  
                    pass
        if counter >= min_msg:
            check = True

        return check
    
    def has_conditional_or_loop(self, msg):

        check = False
        current_id = str(msg)  # Convertimos msg en cadena para evitar errores

        if '.' in current_id:
            current_parts = current_id.split('.')  # Dividimos el ID por puntos (ej. '1.1' -> ['1', '1'])
            # Vamos a buscar los siguientes bloques incrementando la última parte del ID
            next_part = int(current_parts[-1]) + 1  # Incrementamos la última parte
            current_parts[-1] = str(next_part)  # Reemplazamos la última parte con el nuevo valor
            # Ahora construimos el siguiente ID
            parent_id = '.'.join(current_parts)  # Convertimos la lista de nuevo en un ID
            #print(msg)
        else:
            parent_id = str(int(current_id) + 1)

        for substack in self.list_total_blocks:

            if str(substack['id']) == parent_id:
                parent_block = substack['block']  # Asignamos el bloque padre
                # Si encontramos el bloque
                #print(f"Bloque encontrado GENERAL: {parent_block} con ID: {parent_id}")

                break
       
        for block in self.list_total_blocks:
            if(str(block.get('id')) == str(parent_id)):
                    if self.check_conditional(parent_id) or self.check_loops(parent_id):
                        check = True
                        return check


       
        return check
    
    
    def check_nested_conditionals(self):
        """
        Finds if there are any nested conditionals in all the blocks of the script.
        """

        check = False
        print("------------------------sghgshs------------------")
        print(json.dumps(self.list_total_blocks))
        
        for block in self.list_total_blocks:
            if block['block'] == 'doIf' or block['block'] == 'doIfElse':
                try:
                    print("-----------------------logica---------------------------------------------------------")

                    for block_id in block['next']:  # Iterar sobre cada ID en next
                        print("block_id", block_id)
                        if self.has_nested_conditional(block_id):
                            check = True
                            break
                except KeyError:
                    pass

                
        return check    
    
    
    def has_nested_conditional(self, parent_id):
        """
        Returns True if there is a nested conditional
        """
        #print("---------------------------------------------")
        loops = {'doForever', 'doRepeat', 'doUntil'}
        conditionals = {'doIf', 'doIfElse'}

        #print(f"Starting check for nested if from parent_id: {parent_id}")

        # Verifica la estructura de list_total_blocks
        #print(self.list_total_blocks)  # Para asegurarte de la estructura

        parent_block = None  # Inicializamos el bloque padre
        for substack in self.list_total_blocks:
            if substack['id'] == parent_id:
                
                parent_block = substack['block']  # Asignamos el bloque padre
                print("padre", parent_block)

                # Si encontramos el bloque
                #print(f"Bloque encontrado: {parent_block} con ID: {parent_id}")

                break
       
        
      

        # Si es una condición, verificamos los sub-bloques (si los tiene)
        if parent_block in conditionals:
            #(f"Se encontró una condición")
            return True
               
        else: #Si no encuentra un if o else debemos de mirar el 1.1.2
            #print(f"No es un bucle ni una condición. Verificando el siguiente bloque en la jerarquía.")
            current_id = parent_id
            current_parts = current_id.split('.')  # Dividimos el ID por puntos (ej. '1.1' -> ['1', '1'])

            # Vamos a buscar los siguientes bloques incrementando la última parte del ID
            next_part = int(current_parts[-1]) + 1  # Incrementamos la última parte
            current_parts[-1] = str(next_part)  # Reemplazamos la última parte con el nuevo valor

            # Ahora construimos el siguiente ID
            next_id = '.'.join(current_parts)  # Convertimos la lista de nuevo en un ID
            # Verificamos si el siguiente bloque existe y lo procesamos
            next_block = next((block for block in self.list_total_blocks if block["id"] == next_id), None)

            #print(next_block)
            if next_block:
                #print(f"Verificando siguiente bloque con ID: {next_id}")
                if self.has_nested_conditional(next_block['id']):
                    return True


        return False

    
    
    def check_block_sequence(self):

        check = False
        i=0
        for block_dict in self.list_total_blocks:
            i+=1

            if i == self.total_blocks:
                check = True
                break

        return check

    def check_nested_loops(self):
        """
        Finds if there are any nested loops in all the blocks of the script based on block IDs.
        """

        check = False
        for block in self.list_total_blocks:
           
            if block['block'] in {'doForever', 'doRepeat', 'doUntil'}:  # Si es un bucle
                try:
                    # Obtener el ID del bloque

                    for block_id in block['next']:  # Iterar sobre cada ID en next
                        print("--------------------------------------------------------------------------------")
                  
                        if self.has_nested_loops(block_id):  # Verificar si hay bucles anidados basado en ID
                            check = True
                            break
                except KeyError:
                    pass

        return check


    def has_nested_loops(self, parent_id):
        """
        Recursively checks if there are nested loops or conditionals starting from the parent block ID.
        """
        loops = {'doForever', 'doRepeat', 'doUntil'}
        conditionals = {'doIf', 'doIfElse'}
        
        #print(f"Starting check for nested loops from parent_id: {parent_id}")

        # Verifica la estructura de list_total_blocks
        #print(self.list_total_blocks)  # Para asegurarte de la estructura

        parent_block = None  # Inicializamos el bloque padre
        for substack in self.list_total_blocks:
            #print(f"Verificando substack: {substack}")  # Imprime cada substack en la lista
            
            #print(parent_id)
            #print(substack['id'])
            if substack['id'] == parent_id:
                #print("Bloque encontrado")
                parent_block = substack['block']  # Asignamos el bloque padre
                # Si encontramos el bloque
                #print(f"Bloque encontrado: {parent_block} con ID: {parent_id}")

                break
       
        
        # Si es un bucle, retorna True
        if parent_block in loops:
            #print(f"Se encontró un bucle")
            return True

        # Si es una condición, verificamos los sub-bloques (si los tiene)
        elif parent_block in conditionals:
            #print(f"Se encontró una condición")
            
            # Verificamos los bloques siguientes (next)
            next_block_ids = substack['next']
            if next_block_ids:
                #print(f"Verificando siguientes bloques para el bloque if")
                self.has_nested_loops(next_block_ids[0])
               
        else: #Si no encuentra un if o else debemos de mirar el 1.1.2
            #print(f" Comprobando bucles. No es un bucle ni una condición. Verificando el siguiente bloque en la jerarquía.")
            current_id = parent_id
            #print("holaaaa")
            #print(current_id)
            current_parts = current_id.split('.')  # Dividimos el ID por puntos (ej. '1.1' -> ['1', '1'])
            #print("holaaaa")
            # Vamos a buscar los siguientes bloques incrementando la última parte del ID
            next_part = int(current_parts[-1]) + 1  # Incrementamos la última parte
            current_parts[-1] = str(next_part)  # Reemplazamos la última parte con el nuevo valor
            #print("holaaaa")
            # Ahora construimos el siguiente ID
            next_id = '.'.join(current_parts)  # Convertimos la lista de nuevo en un ID
            # Verificamos si el siguiente bloque existe y lo procesamos
            next_block = next((block for block in self.list_total_blocks if block["id"] == next_id), None)
            #print("holaaaa")
           # print(next_block)
            if next_block:
                #print(f"Verificando siguiente bloque con ID: {next_id}")
                if self.has_nested_loops(next_block['id']):
                    return True


        return False
