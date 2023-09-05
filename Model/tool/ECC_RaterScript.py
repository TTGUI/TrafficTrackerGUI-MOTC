import  ECC_Rater

currentClass = ECC_Rater.ECC_Rater()

# args = currentClass.parser.parse_args([
#     '-t', r'E:\Traffic\DataBase_HightRange_Pedestrian\Bule_Gray\RGB\pedestrian_dataset_20230427_part1-label_1.PNG',
#     '-b', r'E:\Traffic\DataBase_HightRange_Pedestrian\BKG\台北市信義區松仁路_信義路五段路口80米_A_3_background.jpg'

#     ])


# args = currentClass.parser.parse_args([
#     '-l', r'C:\Users\Lab602_assistant\Downloads\list.txt',
#     '-t', r'E:\Traffic\DataBase_HightRange_Pedestrian\Bule_Gray\RGB',
#     '-b', r'E:\Traffic\DataBase_HightRange_Pedestrian\BKG'

#     ])
args = currentClass.parser.parse_args([
    '-l', r'C:\Users\Lab602_assistant\Downloads\list_.txt',
    '-t', r'E:\Traffic\DataBase_HightRange_Pedestrian\Bule_Gray\RGB',
    '-b', r'E:\Traffic\DataBase_HightRange_Pedestrian\BKG',
    '-s', "MY"

    ])
currentClass.main(args)

"""
data = ['jelly', 'eng', 90, 'PE', 80, 'art', 815]

def find_highest_score_subject(data_list):
    # 從第二項開始，每隔2項取一次，這樣可以取得所有的科目
    subjects = data_list[1::2]
    
    # 從第三項開始，每隔2項取一次，這樣可以取得所有的分數
    scores = data_list[2::2]
    
    # 使用`max`找出最高分數，然後使用`index`找到該分數在scores列表中的位置
    max_score = max(scores)
    max_score_index = scores.index(max_score)
    
    # 使用上述的索引找到相應的科目
    max_score_subject = subjects[max_score_index]
    
    return max_score_subject, max_score

subject, score = find_highest_score_subject(data)
print(f"最高分數的科目是 {subject}，分數是 {score}。")


"""