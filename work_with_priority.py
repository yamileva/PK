'''
запуск через терминал:    python .\work_with_priority.py 202307181955.json
на выходе создается файл  202307181955_green.json
вывод в консоль можно будет убрать
'''


def calculate_place(applicant_id, num_priority):
    if "consent" in applicants[applicant_id] and applicants[applicant_id]["consent"] != "":
        print("BAD", applicant_id, num_priority)
    if num_priority == len(applicants[applicant_id]['competition_groups_priorities']):
        applicants[applicant_id]["consent"] = 'fail'
        return 'fail'
    priority, gr_id, scoring = applicants[applicant_id]['competition_groups_priorities'][num_priority]
    if len(competition_group_green_stacks[gr_id]) == 0:
        if filtered_competition_groups[gr_id] == 0:
            print("empty group")
            return calculate_place(applicant_id, num_priority + 1)
        competition_group_green_stacks[gr_id].append((scoring, applicant_id))
        applicants[applicant_id]["consent"] = gr_id
        return "ok"
    elif scoring < competition_group_green_stacks[gr_id][-1][0]:
        if len(competition_group_green_stacks[gr_id]) == filtered_competition_groups[gr_id]:
            return calculate_place(applicant_id, num_priority + 1)
        else:
            competition_group_green_stacks[gr_id].append((scoring, applicant_id))
            applicants[applicant_id]["consent"] = gr_id
            return "ok"
    else:
        competition_group_green_stacks[gr_id].append((scoring, applicant_id))
        competition_group_green_stacks[gr_id].sort(reverse=True)
        #for place in range(len(competition_group_green_stacks[gr_id]) - 1, -2, -1):
        #    if place == -1 or scoring < competition_group_green_stacks[gr_id][place][0]:
       #         competition_group_green_stacks[gr_id].insert(place + 1, (scoring, applicant_id))
        applicants[applicant_id]["consent"] = gr_id

        if len(competition_group_green_stacks[gr_id]) > filtered_competition_groups[gr_id]:
            '''
            print(f"Someone is kicked from {gr_id} by {applicant_id}")
            print("before")
            print(f"group {gr_id}, {filtered_competition_groups[gr_id]} places")
            for i in range(len(competition_group_green_stacks[gr_id])):
                print(
                    f"{i}. {competition_group_green_stacks[gr_id][i][1]}, scoring {competition_group_green_stacks[gr_id][i][0]}")
            print("-" * 20)
            '''
            kicked_scoring, kicked_applicant_id = competition_group_green_stacks[gr_id].pop()
            applicants[kicked_applicant_id]["consent"] = ""
            '''
            print("after")
            print(f"{kicked_applicant_id} is kicked")
            print(f"group {gr_id}, {filtered_competition_groups[gr_id]} places")
            for i in range(len(competition_group_green_stacks[gr_id])):
                print(
                    f"{i}. {competition_group_green_stacks[gr_id][i][1]}, scoring {competition_group_green_stacks[gr_id][i][0]}")
            print("-" * 20)
            print("pause")
            input()
            '''
            for kicked_num_priority in range(len(applicants[kicked_applicant_id]['competition_groups_priorities'])):
                if applicants[kicked_applicant_id]['competition_groups_priorities'][kicked_num_priority][1] == gr_id:
                    calculate_place(kicked_applicant_id, kicked_num_priority + 1)
                    return 'ok'


def check_green_stacks():
    all_applicants = set()
    for gr_id in competition_group_green_stacks:
        if len(competition_group_green_stacks[gr_id]) > filtered_competition_groups[gr_id]:
            print(f"Overflow in {gr_id}")
        if len(competition_group_green_stacks[gr_id]) == 0:
            continue
        gr_applicants = {item[1] for item in competition_group_green_stacks[gr_id]}
        if len(all_applicants.intersection(gr_applicants)) != 0:
            print(f"Intersection exists in {gr_id}: {all_applicants.intersection(gr_applicants)}")
        all_applicants = all_applicants.union(gr_applicants)
        if len(gr_applicants) < len(competition_group_green_stacks[gr_id]):
            print(f"Repeat in {gr_id}: {len(gr_applicants)} < {len(competition_group_green_stacks[gr_id])}")
            for item in competition_group_green_stacks[gr_id]:
                if competition_group_green_stacks[gr_id].count(item) > 1:
                    print("---", item, competition_group_green_stacks[gr_id].count(item), 'times')
        prev_item = competition_group_green_stacks[gr_id][0]
        for item in competition_group_green_stacks[gr_id]:
            if item[0] > prev_item[0]:
                print(f"Wrong sequence in {gr_id}: {item} under {prev_item}")
                break
            prev_item = item
    print("competition_group_green_stacks check is completed")
    doppelganger = {}
    for app_id in applicants:
        if applicants[app_id]["consent"] not in ["fail", '']:
            gr_id = applicants[app_id]["consent"]
            if gr_id not in doppelganger:
                doppelganger[gr_id] = {app_id}
            else:
                doppelganger[gr_id].add(app_id)
    for gr_id in doppelganger:
        real_list = {item[1] for item in competition_group_green_stacks[gr_id]}
        if doppelganger[gr_id] != real_list:
            print(f"Error in applicants on {gr_id}:")
            print("--app", doppelganger[gr_id])
            print("--green", real_list)
    print("applicants check is completed")


import sys
import json

'202307181955_mod.json'

with open(sys.argv[1], encoding="utf-8") as jsonfile:
    data = json.load(jsonfile)

'''структура
ex_specialties = {"code": "01.03.04", "name": "Прикладная математика", "education_level": "Бакалавриат"}
ex_entrance_tests = {"specialty_code": "01.03.02", "subject_name": "Математика", "priority": 1}
ex_competition_groups = {
    "id": "000000001",
    "specialty_code": "01.03.02",
    "profile": "Прикладная математика и информатика",
    "institution_name": "УУНиТ",
    "education_form": "Очная",
    "budget_level": "Федеральный бюджет",
    "funding": "Бюджетная основа",
    "category": "Общая",
    "is_military": False,
    "language_code": ""}
ex_admission_plans = {"competition_group_id": 100000001, "number": 30}
ex_number_of_applications = {"competition_group_id": 100000001, "number": 500}
ex_ratings = {
    "competition_group_id": "000000146",
    "position": 45,
    "rank": 0,
    "applicant_id": "201-686-415 43",
    "score_total": 10,
    "score_average": 0,
    "score_subject_1": 0,
    "score_subject_2": 0,
    "score_subject_3": 0,
    "score_achievments": 10,
    "original_submitted": False,
    "consent_submitted": False,
    "consent_count": 0,
    "status": "",
    "note": "",
    "payment_made": False,
    "priority": 2
}'''
filtered_competition_groups = {group["id"]: 0 for group in data['competition_groups']
                               if group['specialty_code'][3:5] in ['03', '04', '05'] and
                               group['funding'] == "Бюджетная основа"}
for group in data['admission_plans']:
    if group['competition_group_id'] in filtered_competition_groups.keys():
        filtered_competition_groups[group['competition_group_id']] = group['number']
applicants = {}
for rating in data['ratings']:
    if rating['competition_group_id'] not in filtered_competition_groups:
        continue
    if not rating["original_submitted"]:
        continue
    if rating["applicant_id"] not in applicants:
        applicants[rating["applicant_id"]] = {
            'max_score_total': int(rating["score_total"]),
            'score_totals': [int(rating["score_total"])],
            'competition_groups_priorities': [(
                int(rating['priority']),
                rating["competition_group_id"],
                (
                    int(rating["score_total"]),
                    int(rating["score_subject_1"]) + int(rating["score_subject_2"]) + int(rating["score_subject_3"]),
                    int(rating["score_subject_1"]),
                    int(rating["score_subject_2"]),
                    int(rating["score_subject_3"])
                )
            )]
        }
    else:
        if int(rating["score_total"]) not in applicants[rating["applicant_id"]]['score_totals']:
            applicants[rating["applicant_id"]]['score_totals'].append(int(rating["score_total"]))
            applicants[rating["applicant_id"]]['max_score_total'] = max(
                applicants[rating["applicant_id"]]['score_totals'])
        applicants[rating["applicant_id"]]['competition_groups_priorities'].append((
            int(rating['priority']),
            rating["competition_group_id"],
            (
                int(rating["score_total"]),
                int(rating["score_subject_1"]) + int(rating["score_subject_2"]) + int(rating["score_subject_3"]),
                int(rating["score_subject_1"]),
                int(rating["score_subject_2"]),
                int(rating["score_subject_3"])
            )
        ))

for key in applicants:
    applicants[key]['competition_groups_priorities'].sort(key=lambda x: (-x[0], x[2], x[1]), reverse=True)

competition_group_green_stacks = {}
for group_id in filtered_competition_groups:
    competition_group_green_stacks[group_id] = []


for applicant_id in sorted(applicants, key=lambda x: applicants[x]['max_score_total'], reverse=True):
    result = calculate_place(applicant_id, 0)


#for applicant_id in sorted(applicants, key=lambda x: applicants[x]['max_score_total']):
    #if applicants[applicant_id]['consent'] == '':
 #       print(applicant_id, applicants[applicant_id])

# Вывод итоговых списков в .out
with open(sys.argv[1].rstrip('.json') + "_lists.out", 'w') as outfile:
    for group_id in competition_group_green_stacks:
        print(f"group {group_id}, {filtered_competition_groups[group_id]} places", file=outfile)
        for i in range(len(competition_group_green_stacks[group_id])):
            print(f"{i + 1}. {competition_group_green_stacks[group_id][i][1]}, scoring {competition_group_green_stacks[group_id][i][0]}", file=outfile)
        print("-" * 20, file=outfile)

check_green_stacks()

for rating_id in range(len(data['ratings'])):
    if data['ratings'][rating_id]["applicant_id"] in applicants and \
            data['ratings'][rating_id]["competition_group_id"] == applicants[data['ratings'][rating_id]["applicant_id"]]["consent"]:
        data['ratings'][rating_id]["consent_submitted"] = True
        # print(data['ratings'][rating_id]["applicant_id"], applicants[data['ratings'][rating_id]["applicant_id"]]["consent"])

with open(sys.argv[1].rstrip('.json')+"_green.json", mode="w", encoding="utf-8") as writefile:
    json.dump(data, writefile, ensure_ascii=False, indent=0)


'''
# проверка повторов приоритетов
for i, (key, value) in enumerate(applicants.items()):
    if sorted([val[0] for val in applicants[key]['competition_groups_priorities']]) != \
            list(range(1, len(applicants[key]['competition_groups_priorities']) + 1)):
        temp = {}
        for val in applicants[key]['competition_groups_priorities']:
            if val[0] in temp:
                if temp[val[0]] != val[1] and abs(int(temp[val[0]]) - int(val[1])) > 2:
                    print(key, ":", applicants[key]['competition_groups_priorities'],
                          "sorted priorities",  sorted([val[0] for val in applicants[key]['competition_groups_priorities']]))
                    break
            else:
                temp[val[0]] = val[1]

# поиск максимального количества разных баллов
max_len_scoring = 0
for i, (key, value) in enumerate(applicants.items()):
    #print(key, " - ", value)
    if len(applicants[key]['score_totals']) > max_len_scoring:
        max_len_scoring = len(applicants[key]['score_totals'])
for i, (key, value) in enumerate(applicants.items()):
    if len(applicants[key]['score_totals']) == max_len_scoring:
        print(key, " - ", value)

print(len(applicants))
print(max_len_scoring)

'''
