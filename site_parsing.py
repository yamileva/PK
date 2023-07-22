import json
from datetime import datetime as dt
from pprint import pprint

def site_reading(ratings, inst_name, sp_code, sp_full_name, site_id, competition_groups_search):
    columns_on_site = ['№', 'Позиция', 'ID поступающего / СНИЛС', 'Балл', 'П1', 'П2', 'П3', 'ИД', 'Приоритет',
                       'Подан оригинал', 'Статус', 'Примечание']
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
    }
    import requests
    api_server_bach = "https://uust.ru/admission/bachelor-and-specialist/ratings/2023/"
    api_server_mag = "https://uust.ru/admission/master/ratings/2023/"

    "https://uust.ru/admission/bachelor-and-specialist/ratings/2023/" \
    "?institution=%D0%A3%D0%A3%D0%9D%D0%B8%D0%A2" \
    "&funding=%D0%91%D1%8E%D0%B4%D0%B6%D0%B5%D1%82%D0%BD%D0%B0%D1%8F+%D0%BE%D1%81%D0%BD%D0%BE%D0%B2%D0%B0" \
    "&education_level=" \
    "&education_form=%D0%9E%D1%87%D0%BD%D0%B0%D1%8F" \
    "&specialty=3"

    "https://uust.ru/admission/master/ratings/2023/" \
    "?funding=%D0%91%D1%8E%D0%B4%D0%B6%D0%B5%D1%82%D0%BD%D0%B0%D1%8F+%D0%BE%D1%81%D0%BD%D0%BE%D0%B2%D0%B0" \
    "&education_form=%D0%9E%D1%87%D0%BD%D0%B0%D1%8F" \
    "&specialty=174"

    columns_bach = [['№', 'position', 'applicant_id', 'score_total', 'score_subject_1', 'score_subject_2',
                     'score_subject_3', 'score_achievments', 'priority', 'original_submitted', 'status', 'note'],
                    ['№', 'position', 'applicant_id', 'score_total', 'score_subject_1', 'score_subject_2',
                     'score_subject_3', 'score_achievments', 'priority', 'original_submitted', 'status', 'payment_made']]
    columns_mag = [['№', 'position', 'applicant_id', 'score_total', 'score_subject_1', 'score_achievments',
                    'priority', 'original_submitted', 'note'],
                   ['№', 'position', 'applicant_id', 'score_total', 'score_subject_1', 'score_achievments',
                    'priority', 'original_submitted', 'payment_made']]
    if sp_code[3:5] != '04':
        params = {
            "institution": inst_name,
            "funding": '',
            "education_level": "",
            'education_form': '',
            'specialty': site_id
        }
        api_server = api_server_bach
        columns = columns_bach
    else:
        params = {
            "institution": inst_name,
            "funding": '',
            'education_form': '',
            'specialty': site_id
        }
        api_server = api_server_mag
        columns = columns_mag
    response = requests.get(api_server, params=params)
    if not response:
        print("response error")
        return

    # print("$$$", inst_name, sp_code, sp_full_name, site_id)
    # print(response.url)
    html_str = response.content.decode(encoding='utf-8', errors='strict').split('\n')
    # print(*html_str, sep="\n")
    is_table = False
    col_num = 0
    id_group, category = "", ""
    # first_head = True
    for line in html_str:
        try:
            line = line.strip()
            if line.startswith('<h3'):
                is_table = True
                new_part = line[line.find(">") + 1:-(len('</h3>'))]
                #print("$$$", inst_name, funding, edu_form, sp_code)
                #print(new_part)
                #print(new_part[:new_part.find(inst_name)])
                #if sp_code == "13.03.02":
                #    print(new_part)
                #    print(new_part[:new_part.find(inst_name)])
                #    print(new_part[:new_part.find(inst_name)][len(sp_full_name):])
                profile = new_part[:new_part.find(inst_name)][len(sp_full_name):].strip(" ,")[1:-1].replace('&quot;', '"')
                #print(profile)
                #print(new_part.split('(')[1].split(")")[1].split(", "))
                edu_form, funding, category = new_part[new_part.find(inst_name):].split(", ")[1:4]
                #print(funding, edu_form, category)
                id_group = competition_groups_search[inst_name][sp_code][funding][edu_form]['profiles'][
                    (profile, category)]
                #print(id_group)
                #print("-------------")
            elif line.startswith('</table>'):
                is_table = False
            # elif line.startswith('<th>') and first_head:
            # columns.append(line.lstrip('<th>').rstrip('</th>'))
            # elif line.startswith('</thead>') and first_head:
            # first_head = False
            elif is_table and line.startswith('<tr>'):
                col_num = 0
            elif is_table and line.startswith('<td>'):
                if col_num >= len(columns[0]):
                    print(col_num, line)
                    col_num = 0
                if col_num == 0:
                    ratings.append({
                        'competition_group_id': id_group,
                        "position": 0,
                        "rank": 0,
                        "applicant_id": "",
                        "score_total": 0,
                        "score_average": 0,
                        "score_subject_1": 0,
                        "score_subject_2": 0,
                        "score_subject_3": 0,
                        "score_achievments": 0,
                        "original_submitted": False,
                        "consent_submitted": False,
                        "consent_count": 0,
                        "status": "",
                        "note": "",
                        "priority": 100
                    })
                value = line[len('<td>'):-len('</td>')]
                if value == 'Да':
                    value = True
                elif value == 'Нет':
                    value = False
                if category == 'Контракт':
                    ratings[-1][columns[1][col_num]] = value
                else:
                    ratings[-1][columns[0][col_num]] = value
                col_num += 1
        except Exception as e:
            print("Исключение:", e, "на строке", line, "info", inst_name, sp_code, sp_full_name, site_id)

    # pprint(ratings)

def calculate_place(applicant_id, num_priority,
                    applicants, competition_group_green_stacks, filtered_competition_groups):
    if "consent" in applicants[applicant_id] and applicants[applicant_id]["consent"] != "":
        print("BAD", applicant_id, num_priority)
    if num_priority == len(applicants[applicant_id]['competition_groups_priorities']):
        applicants[applicant_id]["consent"] = 'fail'
        return 'fail'
    priority, gr_id, scoring = applicants[applicant_id]['competition_groups_priorities'][num_priority]
    if len(competition_group_green_stacks[gr_id]) == 0:
        if filtered_competition_groups[gr_id] == 0:
            print("empty group")
            return calculate_place(applicant_id, num_priority + 1,
                    applicants, competition_group_green_stacks, filtered_competition_groups)
        competition_group_green_stacks[gr_id].append((scoring, applicant_id))
        applicants[applicant_id]["consent"] = gr_id
        return "ok"
    elif scoring < competition_group_green_stacks[gr_id][-1][0]:
        if len(competition_group_green_stacks[gr_id]) == filtered_competition_groups[gr_id]:
            return calculate_place(applicant_id, num_priority + 1,
                    applicants, competition_group_green_stacks, filtered_competition_groups)
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
                    calculate_place(kicked_applicant_id, kicked_num_priority + 1,
                                    applicants, competition_group_green_stacks, filtered_competition_groups)
                    return 'ok'


def check_green_stacks(competition_group_green_stacks, filtered_competition_groups, applicants):
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



def calculate_ratings(ratings, filtered_competition_groups, special_competition_groups):
    applicants = {}
    for rating in ratings:
        try:
            if rating['competition_group_id'] not in filtered_competition_groups:
                continue
            if not rating["original_submitted"]:
                continue

            modified_total_score = int(rating["score_total"])
            if special_competition_groups[rating['competition_group_id']]:
                modified_priority = int(rating['priority'])
            elif rating['note'] == "Без вступительных испытаний":
                modified_priority = 0
                modified_total_score = 500
            else:
                modified_priority = int(rating['priority']) + 100
            if rating["applicant_id"] not in applicants:
                applicants[rating["applicant_id"]] = {
                    'max_score_total': modified_total_score,
                    'score_totals': [modified_total_score],
                    'competition_groups_priorities': [(
                        modified_priority,
                        rating["competition_group_id"],
                        (
                            modified_total_score,
                            int(rating["score_subject_1"]) + int(rating["score_subject_2"]) + int(
                                rating["score_subject_3"]),
                            int(rating["score_subject_1"]),
                            int(rating["score_subject_2"]),
                            int(rating["score_subject_3"])
                        )
                    )]
                }
            else:
                if int(rating["score_total"]) not in applicants[rating["applicant_id"]]['score_totals']:
                    applicants[rating["applicant_id"]]['score_totals'].append(modified_total_score)
                    applicants[rating["applicant_id"]]['max_score_total'] = max(
                        applicants[rating["applicant_id"]]['score_totals'])
                applicants[rating["applicant_id"]]['competition_groups_priorities'].append((
                    modified_priority,
                    rating["competition_group_id"],
                    (
                        modified_total_score,
                        int(rating["score_subject_1"]) + int(rating["score_subject_2"]) + int(rating["score_subject_3"]),
                        int(rating["score_subject_1"]),
                        int(rating["score_subject_2"]),
                        int(rating["score_subject_3"])
                    )
                ))
        except Exception as e:
            print("Exception", e)
            print("no key in rating", rating)

    for key in applicants:
        applicants[key]['competition_groups_priorities'].sort(key=lambda x: (-x[0], x[2], x[1]), reverse=True)

    competition_group_green_stacks = {}
    for group_id in filtered_competition_groups:
        competition_group_green_stacks[group_id] = []

    for applicant_id in sorted(applicants, key=lambda x: applicants[x]['max_score_total'], reverse=True):
        result = calculate_place(applicant_id, 0,
                                 applicants, competition_group_green_stacks, filtered_competition_groups)

    # for applicant_id in sorted(applicants, key=lambda x: applicants[x]['max_score_total']):
    # if applicants[applicant_id]['consent'] == '':
    #       print(applicant_id, applicants[applicant_id])

    # Вывод итоговых списков в .out

    check_green_stacks(competition_group_green_stacks, filtered_competition_groups, applicants)

    return applicants, competition_group_green_stacks

def print_out(data_competition_groups, competition_group_green_stacks, filtered_competition_groups):
    competition_groups = {}
    for group in data_competition_groups:
        if group['id'] in competition_group_green_stacks:
            competition_groups[group['id']] = {
                "specialty_code": group["specialty_code"],
                "profile": group["profile"],
                "institution_name": group["institution_name"],
                "education_form": group["education_form"],
                "funding": group["funding"],
                "category": group["category"]
            }
    datenow = dt.now().strftime("%m.%d..%H.%M")
    with open('result_data/' + datenow + "_lists.out", 'w', encoding="utf-8") as outfile:
        for group_id in competition_group_green_stacks:
            # print(f"group {group_id}, ", file=outfile)
            print(competition_groups[group_id]["specialty_code"],
                  competition_groups[group_id]["profile"],
                  competition_groups[group_id]["institution_name"],
                  competition_groups[group_id]["education_form"],
                  competition_groups[group_id]["funding"],
                  competition_groups[group_id]["category"],
                  sep=', ', file=outfile)
            print(
                f"План {filtered_competition_groups[group_id]} мест, текущая заполненность {len(competition_group_green_stacks[group_id])}",
                file=outfile)
            for i in range(len(competition_group_green_stacks[group_id])):
                print(
                    f"{i + 1}. {competition_group_green_stacks[group_id][i][1]}, scoring {competition_group_green_stacks[group_id][i][0]}",
                    file=outfile)
            print("-" * 20, file=outfile)

    with open('result_data/' + datenow + "_brief.csv", 'w', encoding="utf-8") as outfile:
        print("specialty_code", "profile", "institution_name", "education_form", "funding", "category",
              'plan_places', "current_places", "fraction", sep=';', file=outfile)
        for group_id in competition_group_green_stacks:
            print("Sp " + competition_groups[group_id]["specialty_code"],
                  competition_groups[group_id]["profile"],
                  competition_groups[group_id]["institution_name"],
                  competition_groups[group_id]["education_form"],
                  competition_groups[group_id]["funding"],
                  competition_groups[group_id]["category"],
                  filtered_competition_groups[group_id],
                  len(competition_group_green_stacks[group_id]),
                  0 if filtered_competition_groups[group_id] == 0
                  else len(competition_group_green_stacks[group_id]) / filtered_competition_groups[group_id],
                  sep=';', file=outfile)

def main():
    print("Begin in", dt.now())
    json_name = "init.json"
    with open(json_name, encoding="utf-8") as jsonfile:
        data = json.load(jsonfile)


    filtered_competition_groups = {group["id"]: 0 for group in data['competition_groups']
                                   if group['specialty_code'][3:5] in ['03', '04', '05'] and
                                   group['funding'] == "Бюджетная основа"}
    special_competition_groups = {group["id"]: (group["category"] in ["Особая", "Отдельная"])
                                  for group in data['competition_groups']
                                  if group['specialty_code'][3:5] in ['03', '04', '05'] and
                                  group['funding'] == "Бюджетная основа"}
    for group in data['admission_plans']:
        if group['competition_group_id'] in filtered_competition_groups.keys():
            filtered_competition_groups[group['competition_group_id']] = group['number']



    ex_competition_groups = {
        "id": "000000001",
        "specialty_code": "01.03.02",                       # 2
        "profile": "Прикладная математика и информатика",   # 5
        "institution_name": "УУНиТ",                        # 1
        "education_form": "Очная",                          # 4
        "budget_level": "Федеральный бюджет",               # -
        "funding": "Бюджетная основа",                      # 3
        "category": "Общая",                                # 6
        "is_military": False,
        "language_code": ""}

    specialities_on_site = {}
    specialities_full_names = {}
    with open("init_data/example_init_bach.htm", 'r', encoding="utf-8") as html_ex:
        is_sp_found = False
        for line in html_ex:
            if "Направление/специальность" in line:
                is_sp_found = True
            if not is_sp_found:
                continue
            if '<option' in line:
                p_line = line.lstrip('<option value="').replace('">', ' ').split(" ")
                # print(p_line)
                if len(p_line) > 1 and len(p_line[1]) == 8:
                    specialities_on_site[p_line[1]] = p_line[0]
                    fullname = line.split("<")[1].split(">")[1]
                    specialities_full_names[p_line[1]] = fullname

    with open("init_data/example_init_mag.htm", 'r', encoding="utf-8") as html_ex:
        is_sp_found = False
        for line in html_ex:
            if "Направление/специальность" in line:
                is_sp_found = True
            if not is_sp_found:
                continue
            if '<option' in line:
                p_line = line.lstrip('<option value="').replace('">', ' ').split(" ")
                # print(p_line)
                if len(p_line) > 1 and len(p_line[1]) == 8:
                    specialities_on_site[p_line[1]] = p_line[0]
                    fullname = line.split("<")[1].split(">")[1]
                    specialities_full_names[p_line[1]] = fullname

    #pprint(specialities_on_site)
    #pprint(specialities_full_names)

    competition_groups_search = {}
    for group in data['competition_groups']:
        if group['specialty_code'][3:5] not in ['03', '04', '05']:
            continue
        inst_name = group["institution_name"]
        if inst_name not in competition_groups_search:                                  # 1
            competition_groups_search[inst_name] = {}
        sp_code = group['specialty_code']
        if sp_code not in competition_groups_search[inst_name]:                         # 2
            competition_groups_search[inst_name][sp_code] = {}
        funding = group["funding"]
        if funding not in competition_groups_search[inst_name][sp_code]:                         # 3
            competition_groups_search[inst_name][sp_code][funding] = {}
        edu_form = group["education_form"]
        if edu_form not in competition_groups_search[inst_name][sp_code][funding]:               # 4
            competition_groups_search[inst_name][sp_code][funding][edu_form] = {'site_id': specialities_on_site[sp_code],
                                                                                'profiles': {}}

        profile = group['profile']
        category = group['category']
        if group['is_military']:
            category += " (Минобрнауки России)"
        competition_groups_search[inst_name][sp_code][funding][edu_form]['profiles'][(profile, category)] = group['id']
    #pprint(competition_groups_search)
    #with open("specialities.txt", 'w', encoding='utf-8') as spec:
        #print(competition_groups_search, file=spec)
    print(dt.now(), "dicts are created")
    #'''

    ratings = []
    # inst_name, funding, edu_form, sp_code = 'УУНиТ', "Бюджетная основа", "Очная", '01.03.04'
    # site_id = competition_groups_search[inst_name][funding][edu_form][sp_code]['site_id']
    # site_reading(ratings, inst_name, funding, edu_form,
    # sp_code, specialities_full_names[sp_code], site_id, competition_groups_search)
    # pprint(ratings)
    for inst_name in competition_groups_search:
        #for funding in competition_groups_search[inst_name]:
            #for edu_form in competition_groups_search[inst_name][funding]:
                #for sp_code in competition_groups_search[inst_name][funding][edu_form]:
                    #site_id = competition_groups_search[inst_name][funding][edu_form][sp_code]['site_id']

        for sp_code in competition_groups_search[inst_name]:
            site_id = specialities_on_site[sp_code]
            site_reading(ratings, inst_name, sp_code, specialities_full_names[sp_code], site_id,
                         competition_groups_search)

    print(dt.now(), "ratings are created with len", len(ratings))
    #pprint(ratings[:10])
    datenow = dt.now().strftime("%m.%d..%H.%M")
    with open("result_data/" + datenow + "ratings.json", mode="w", encoding="utf-8") as writefile:
        json.dump(ratings, writefile, ensure_ascii=False, indent=0)
    print(dt.now(), "ratings are written")

    '''
    #calculate_ratings(data['ratings'], filtered_competition_groups, special_competition_groups)
    with open("ratings_reserve.json", mode="r", encoding="utf-8") as writefile:
        ratings = json.load(writefile)
    '''
    applicants, competition_group_green_stacks = calculate_ratings(ratings, filtered_competition_groups,
                                                                   special_competition_groups)
    print(dt.now(), "ratings with greens are calculated")
    for rating_id in range(len(ratings)):
        if ratings[rating_id]["applicant_id"] in applicants and \
                ratings[rating_id]["competition_group_id"] == \
                applicants[ratings[rating_id]["applicant_id"]]["consent"]:
            ratings[rating_id]["consent_submitted"] = True
            # print(data['ratings'][rating_id]["applicant_id"], applicants[result_data['ratings'][rating_id]["applicant_id"]]["consent"])

    #with open(sys.argv[1].rstrip('.json') + "_green.json", mode="w", encoding="utf-8") as writefile:
        #json.dump(data, writefile, ensure_ascii=False, indent=0)
    print_out(data['competition_groups'], competition_group_green_stacks, filtered_competition_groups)
    print(dt.now(), "ratings with greens are written")

if __name__ == "__main__":
    main()

