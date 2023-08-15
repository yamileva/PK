import json
import sys
from datetime import datetime as dt
from pprint import pprint


def main_parsing(logout):
    print("Begin in", dt.now(), file=logout)
    json_name = "init.json"
    with open("init_data/" + json_name, encoding="utf-8") as jsonfile:
        data = json.load(jsonfile)

    all_competition_groups = {group["id"]: 0 for group in data['competition_groups']
                              if group['specialty_code'][3:5] in ['03', '04', '05'] and
                              group['funding'] == "Бюджетная основа" }

    filtered_competition_groups = {group["id"]: 0 for group in data['competition_groups']
                                   if (group['specialty_code'][3:5] in ['03', '05'] and
                                   group['funding'] == "Бюджетная основа" and group['category'] == "Общая") or
                                   (group['specialty_code'][3:5] == '04' and group['funding'] == "Бюджетная основа" and
                                    group['category'] in ["Общая", "Целевая"])}
    special_competition_groups = {group["id"]: (group["category"] in ["Особая", "Отдельная", "Целевая"])
                                  for group in data['competition_groups']
                                  if (group['specialty_code'][3:5] in ['03', '05'] and
                                      group['funding'] == "Бюджетная основа" and group['category'] == "Общая") or
                                  (group['specialty_code'][3:5] == '04' and group['funding'] == "Бюджетная основа" and
                                   group['category'] in ["Общая", "Целевая"])}

    competition_groups = {}  # info by group_id
    common_competition_groups = {}  # group_id by profile, category by speciality code
    mag_goal_to_common = {}
    for group in data['competition_groups']:
        if group['id'] in filtered_competition_groups:
            competition_groups[group['id']] = {
                "specialty_code": group["specialty_code"].strip(),
                "profile": group["profile"].strip(),
                "institution_name": group["institution_name"].strip(),
                "education_form": group["education_form"].strip(),
                "funding": group["funding"].strip(),
                "category": group["category"].strip() +
                            (" (Минобрнауки России)" if group['is_military'] else "")
            }
            if group["category"] == "Общая":
                if (group["specialty_code"].strip(), group["profile"].strip()) not in common_competition_groups:

                    common_competition_groups[(group["specialty_code"].strip(), group["profile"].strip())] = {
                        group["education_form"].strip(): group['id']
                    }
                else:
                    if group["education_form"].strip() in common_competition_groups[(group["specialty_code"].strip(), group["profile"].strip())]:
                        print("repeat", (group["profile"].strip(), group["education_form"].strip()), file=logout)
                    else:
                        common_competition_groups[(group["specialty_code"].strip(), group["profile"].strip())][group["education_form"].strip()] = group['id']
            if group['specialty_code'][3:5] == '04' and group['funding'] == "Бюджетная основа" and \
                    group['category'] == "Целевая":
                mag_goal_to_common[group["id"]] = (group["specialty_code"].strip(),
                                                   group["profile"].strip(),
                                                   # group["institution_name"].strip(),
                                                   group["education_form"].strip())

    for group_id, item in mag_goal_to_common.items():
        mag_goal_to_common[group_id] = common_competition_groups[(item[0], item[1])][item[2]]

    for group in data['admission_plans']:
        if group['competition_group_id'] in filtered_competition_groups.keys():
            filtered_competition_groups[group['competition_group_id']] = group['number']

    with open("init_data/init_bach_groups.htm", 'r', encoding="utf-8") as html_str:

        columns_bach = ['№', 'sp', 'profile', 'plan', 'granted', 'deleted',
                        'vacant', 'apps', 'originals', 'KPO', 'KPZ']
        is_table = False

        for line in html_str:
            try:
                line = line.strip()
                if line.startswith('<h4'):
                    is_table = True
                    new_part = line[line.find(">") + 1:-(len('</h4>'))]
                    inst_name, edu_form, funding = new_part.split(", ")[1:4]
                elif line.startswith('</table>'):
                    is_table = False

                elif is_table and line.startswith('<tr'):
                    row = []
                elif is_table and line.startswith('<td'):
                    if len(row) >= len(columns_bach):
                        print("error", line, file=logout)
                        row = []
                    value = line[len('<td>'):-len('</td>')]
                    row.append(value)
                elif is_table and line.startswith('</tr'):
                    if len(row) != 0:
                        sp_code = row[1].split()[0]
                        profile = row[2]
                        stack_len = int(row[6])
                        if funding == "Бюджетная основа":
                            group_id = common_competition_groups[(sp_code, profile)][edu_form]
                            filtered_competition_groups[group_id] = stack_len


            except Exception as e:
                print("Исключение:", e, "на строке", line,
                      file=logout)

    # извлечение списка направлений из страницы - из выпадающего списка, в т.ч. полное название и номер для запроса
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
                if len(p_line) > 1 and len(p_line[1]) == 8:
                    specialities_on_site[p_line[1]] = p_line[0]
                    fullname = line.split("<")[1].split(">")[1]
                    specialities_full_names[p_line[1]] = fullname

    # извлечение списка направлений из страницы - из выпадающего списка, в т.ч. полное название и номер для запроса
    with open("init_data/example_init_mag.htm", 'r', encoding="utf-8") as html_ex:
        is_sp_found = False
        for line in html_ex:
            if "Направление/специальность" in line:
                is_sp_found = True
            if not is_sp_found:
                continue
            if '<option' in line:
                p_line = line.lstrip('<option value="').replace('">', ' ').split(" ")
                if len(p_line) > 1 and len(p_line[1]) == 8:
                    specialities_on_site[p_line[1]] = p_line[0]
                    fullname = line.split("<")[1].split(">")[1]
                    specialities_full_names[p_line[1]] = fullname

    # извлечение направлений с категориями из init.json, в т.ч. идентификационного номера пары и профилей
    competition_groups_search = {}
    for group in data['competition_groups']:
        if group['specialty_code'][3:5] not in ['03', '04', '05']:
            continue
        inst_name = group["institution_name"].strip()
        if inst_name not in competition_groups_search:  # 1
            competition_groups_search[inst_name] = {}
        sp_code = group['specialty_code'].strip()
        if sp_code not in competition_groups_search[inst_name]:  # 2
            competition_groups_search[inst_name][sp_code] = {}
        funding = group["funding"].strip()
        if funding not in competition_groups_search[inst_name][sp_code]:  # 3
            competition_groups_search[inst_name][sp_code][funding] = {}
        edu_form = group["education_form"].strip()
        if edu_form not in competition_groups_search[inst_name][sp_code][funding]:  # 4
            competition_groups_search[inst_name][sp_code][funding][edu_form] = {
                'site_id': specialities_on_site[sp_code], 'profiles': {}}

        profile = group['profile'].strip()
        category = group['category'].strip()
        if group['is_military']:
            category += " (Минобрнауки России)"
        competition_groups_search[inst_name][sp_code][funding][edu_form]['profiles'][(profile, category)] = group['id']

    print(dt.now(), "dicts are created", file=logout)


    ratings = []

    # inst_name, funding, edu_form, sp_code = 'УУНиТ', "Бюджетная основа", "Очная", '01.03.04'
    # site_id = competition_groups_search[inst_name][funding][edu_form][sp_code]['site_id']
    # site_reading(ratings, inst_name, funding, edu_form,
    # sp_code, specialities_full_names[sp_code], site_id, competition_groups_search)
    # pprint(ratings)

    # '''  for reading instead site parsing
    for inst_name in competition_groups_search:
        for sp_code in competition_groups_search[inst_name]:
            site_id = specialities_on_site[sp_code]
            try:
                result = site_reading(ratings, inst_name, sp_code, specialities_full_names[sp_code], site_id,
                                      competition_groups_search, filtered_competition_groups, logout)
                if result == 500:
                    return
            except Exception as e:
                print("exception on response", e, file=logout)
                return


    print(dt.now(), "ratings are created with len", len(ratings), file=logout)

    datenow = dt.now().strftime("%m.%d..%H.%M")
    with open("result_data/ratings.json", mode="w", encoding="utf-8") as writefile:
        json.dump(ratings, writefile, ensure_ascii=False, indent=0)
    print(dt.now(), "ratings are written", file=logout)

    '''
    #calculate_ratings(data['ratings'], filtered_competition_groups, special_competition_groups)
    with open("result_data/ratings.json", mode="r", encoding="utf-8") as writefile:
        ratings = json.load(writefile)
    datenow = dt.now().strftime("%m.%d..%H.%M")
    '''
    granted = []
    applicants, competition_group_green_stacks = calculate_ratings(ratings, filtered_competition_groups,
                                                                   special_competition_groups, mag_goal_to_common,
                                                                   granted, logout)
    print(dt.now(), "ratings with greens are calculated", file=logout)
    with open("result_data/granted.txt", mode='w', encoding="utf-8") as writefile:
        print(*granted, sep="\n", file=writefile)

    with open("result_data/greens.txt", mode='w', encoding="utf-8") as writefile:
        print(competition_group_green_stacks, file=writefile)

    for rating_id in range(len(ratings)):
        if ratings[rating_id]["applicant_id"] in applicants and \
                ratings[rating_id]["competition_group_id"] == \
                applicants[ratings[rating_id]["applicant_id"]]["consent"]:
            ratings[rating_id]["consent_submitted"] = True

    competition_group_white_stacks, applicants_json = calculate_white_stacks(ratings, filtered_competition_groups,
                                                                             granted)

    with open("result_data/whites.txt", mode='w', encoding="utf-8") as writefile:
        print(competition_group_white_stacks, file=writefile)

    with open("result_data/granted_after.txt", mode='w', encoding="utf-8") as writefile:
        print(*granted, sep="\n", file=writefile)

    # data['ratings'] = ratings
    # with open("result_data/ratings_green.json", mode="w", encoding="utf-8") as writefile:
    # json.dump(data, writefile, ensure_ascii=False, indent=0)



    # applicants_json = {applicant_id: [(item[0], item[1], item[2], applicants[applicant_id]['consent'] == item[1])
    #                                  for item in applicants[applicant_id]['competition_groups_priorities']]
    #                   for applicant_id in applicants}
    """ modified_priority, group_id, scoring(5*int), consent """
    json_stacks = [competition_groups, filtered_competition_groups, competition_group_green_stacks,
                   competition_group_white_stacks, applicants_json]
    with open("result_data/ratings_stacks.json", mode="w", encoding="utf-8") as writefile:
        json.dump(json_stacks, writefile, ensure_ascii=False, indent=0)

    if __name__ == "__main__":
        print_out(datenow, competition_groups, competition_group_green_stacks, filtered_competition_groups,
                  competition_group_white_stacks)

    print(dt.now(), "ratings with greens are written", file=logout)
    return datenow


def site_reading(ratings, inst_name, sp_code, sp_full_name, site_id,
                 competition_groups_search, filtered_competition_groups, logout):

    import requests
    api_server_bach = "https://uust.ru/admission/bachelor-and-specialist/ratings/2023/"
    api_server_mag = "https://uust.ru/admission/master/ratings/2023/"

    columns_bach = [['№', 'position', 'applicant_id', 'score_total', 'score_subject_1', 'score_subject_2',
                     'score_subject_3', 'score_achievments', 'priority', 'original_submitted', 'status', 'note'],
                    ['№', 'position', 'applicant_id', 'score_total', 'score_subject_1', 'score_subject_2',
                     'score_subject_3', 'score_achievments', 'priority', 'original_submitted', 'status', 'payment_made']]
    columns_mag = [['№', 'position', 'applicant_id', 'score_total', 'score_subject_1', 'score_achievments',
                    'priority', 'original_submitted', 'status', 'note'],
                   ['№', 'position', 'applicant_id', 'score_total', 'score_subject_1', 'score_achievments',
                    'priority', 'original_submitted', 'status', 'payment_made']]
    if sp_code[3:5] != '04':
        params = {
            "institution": inst_name,
            "funding": 'Бюджетная основа',
            "education_level": "",
            'education_form': '',
            'specialty': site_id
        }
        api_server = api_server_bach
        columns = columns_bach
    else:
        params = {
            "institution": inst_name,
            "funding": 'Бюджетная основа',
            'education_form': '',
            'specialty': site_id
        }
        api_server = api_server_mag
        columns = columns_mag
    response = requests.get(api_server, params=params)
    if not response:
        print("response error", file=logout)
        return 500

    # print(response.url, file=logout)
    html_str = response.content.decode(encoding='utf-8', errors='strict').split('\n')
    is_table = False
    col_num = 0
    id_group, category = "", ""
    title_inits = False
    # first_head = True
    for line in html_str:
        try:
            line = line.strip()
            if line.startswith('<h3'):
                new_part = line[line.find(">") + 1:-(len('</h3>'))]
                if new_part and new_part[0].isdigit():
                    is_table = True
                    edu_form, funding, category = new_part[new_part.find(inst_name):].split(", ")[1:4]
                    title_inits = True
            elif title_inits and line.startswith('<h4'):
                new_part = line[line.find(">") + 1:-(len('</h4>'))].strip()
                profile = new_part[new_part.find(":") + 1:].strip().replace('&quot;', '"')
                try:
                    id_group = competition_groups_search[inst_name][sp_code][funding][edu_form]['profiles'][
                            (profile, category)]
                except Exception as e:
                    print("Исключение:", e, "на строке", line, "info", inst_name, sp_code, (profile, category),
                          file=logout)
                    return
            elif line.startswith('</table>'):
                is_table = False
            elif is_table and "Всего мест:" in line:
                place_count = int(line[line.find(":") + 1:line.find(".")].strip())
                # filtered_competition_groups[id_group] = place_count

            elif is_table and line.startswith('<tr'):
                col_num = 0
            elif is_table and line.startswith('<td'):
                if col_num >= len(columns[0]):
                    print(sp_code, col_num, line, file=logout)
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
            print("Исключение:", e, "на строке", line, "info", inst_name, sp_code, sp_full_name, site_id, file=logout)


def calculate_place(applicant_id, num_priority,
                    applicants, competition_group_green_stacks, filtered_competition_groups, logout):
    if "consent" in applicants[applicant_id] and applicants[applicant_id]["consent"] != "":
        print("BAD", applicant_id, num_priority, file=logout)
    if num_priority == len(applicants[applicant_id]['competition_groups_priorities']):
        applicants[applicant_id]["consent"] = 'fail'
        return 'fail'
    priority, gr_id, scoring, note = applicants[applicant_id]['competition_groups_priorities'][num_priority]
    if len(competition_group_green_stacks[gr_id]) == 0:
        if filtered_competition_groups[gr_id] == 0:
            print("empty group", gr_id, file=logout)
            return calculate_place(applicant_id, num_priority + 1,
                                   applicants, competition_group_green_stacks, filtered_competition_groups, logout)
        competition_group_green_stacks[gr_id].append((scoring, applicant_id, note))
        applicants[applicant_id]["consent"] = gr_id
        return "ok"
    elif scoring < competition_group_green_stacks[gr_id][-1][0]:
        if len(competition_group_green_stacks[gr_id]) == filtered_competition_groups[gr_id]:
            return calculate_place(applicant_id, num_priority + 1,
                                   applicants, competition_group_green_stacks, filtered_competition_groups, logout)
        else:
            competition_group_green_stacks[gr_id].append((scoring, applicant_id, note))
            applicants[applicant_id]["consent"] = gr_id
            return "ok"
    else:
        competition_group_green_stacks[gr_id].append((scoring, applicant_id, note))
        competition_group_green_stacks[gr_id].sort(reverse=True)
        # for place in range(len(competition_group_green_stacks[gr_id]) - 1, -2, -1):
        #    if place == -1 or scoring < competition_group_green_stacks[gr_id][place][0]:
        #        competition_group_green_stacks[gr_id].insert(place + 1, (scoring, applicant_id))
        applicants[applicant_id]["consent"] = gr_id

        if len(competition_group_green_stacks[gr_id]) > filtered_competition_groups[gr_id]:
            kicked_scoring, kicked_applicant_id, _ = competition_group_green_stacks[gr_id].pop()
            applicants[kicked_applicant_id]["consent"] = ""
            for kicked_num_priority in range(len(applicants[kicked_applicant_id]['competition_groups_priorities'])):
                if applicants[kicked_applicant_id]['competition_groups_priorities'][kicked_num_priority][1] == gr_id:
                    calculate_place(kicked_applicant_id, kicked_num_priority + 1,
                                    applicants, competition_group_green_stacks, filtered_competition_groups, logout)
                    return 'ok'


def check_green_stacks(competition_group_green_stacks, filtered_competition_groups, applicants, logout):
    all_applicants = set()
    for gr_id in competition_group_green_stacks:
        if len(competition_group_green_stacks[gr_id]) > filtered_competition_groups[gr_id]:
            print(f"Overflow in {gr_id}", file=logout)
        if len(competition_group_green_stacks[gr_id]) == 0:
            continue
        gr_applicants = {item[1] for item in competition_group_green_stacks[gr_id]}
        if len(all_applicants.intersection(gr_applicants)) != 0:
            print(f"Intersection exists in {gr_id}: {all_applicants.intersection(gr_applicants)}", file=logout)
        all_applicants = all_applicants.union(gr_applicants)
        if len(gr_applicants) < len(competition_group_green_stacks[gr_id]):
            print(f"Repeat in {gr_id}: {len(gr_applicants)} < {len(competition_group_green_stacks[gr_id])}",
                  file=logout)
            for item in competition_group_green_stacks[gr_id]:
                if competition_group_green_stacks[gr_id].count(item) > 1:
                    print("---", item, competition_group_green_stacks[gr_id].count(item), 'times', file=logout)
        prev_item = competition_group_green_stacks[gr_id][0]
        for item in competition_group_green_stacks[gr_id]:
            if item[0] > prev_item[0]:
                print(f"Wrong sequence in {gr_id}: {item} under {prev_item}", file=logout)
                break
            prev_item = item
    print("competition_group_green_stacks check is completed", file=logout)
    doppelganger = {}
    for app_id in applicants:
        if "consent" not in applicants[app_id]:
            print("no consent", app_id)
            continue
        if applicants[app_id]["consent"] not in ["fail", '']:
            gr_id = applicants[app_id]["consent"]
            if gr_id not in doppelganger:
                doppelganger[gr_id] = {app_id}
            else:
                doppelganger[gr_id].add(app_id)
    for gr_id in doppelganger:
        real_list = {item[1] for item in competition_group_green_stacks[gr_id]}
        if doppelganger[gr_id] != real_list:
            print(f"Error in applicants on {gr_id}:", file=logout)
            print("--app", doppelganger[gr_id], file=logout)
            print("--green", real_list, file=logout)
    print("applicants check is completed", file=logout)


def calculate_ratings(ratings, filtered_competition_groups, special_competition_groups,
                      mag_goal_to_common, granted, logout):
    applicants = {}

    for rating in ratings:
        try:
            if rating["applicant_id"].isspace():
                print("Empty applicant", rating)
                continue
            if rating["status"] == 'Зачислен':
                granted.append(rating['applicant_id'])
                if rating["applicant_id"] in applicants:
                    del applicants[rating["applicant_id"]]
                continue
            if rating["applicant_id"] in granted:
                continue
            if rating['competition_group_id'] not in filtered_competition_groups:
                continue

            if not rating["original_submitted"]:
                continue

            modified_total_score = int(rating["score_total"])
            if modified_total_score < 25:
                continue
            if special_competition_groups[rating['competition_group_id']]:
                modified_priority = int(rating['priority'])
            #elif rating['note'] == "Без вступительных испытаний":
            #    modified_priority = 0
            #    modified_total_score = 500
            else:
                modified_priority = int(rating['priority']) + 100
            if int(rating["score_subject_1"]) == 0 or \
                    int(rating["score_subject_2"]) == 0 or \
                    int(rating["score_subject_3"]) == 0:
                modified_priority += 1000
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
                        ),
                        rating["note"].replace('&quot;', '"') + " " + rating["status"]
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
                    ),
                    rating["note"].replace('&quot;', '"') + " " + rating["status"]
                ))
        except Exception as e:
            print("Exception", e, file=logout)
            print("no key in rating", rating, file=logout)

    for key in applicants:
        applicants[key]['competition_groups_priorities'].sort(key=lambda x: (-x[0], x[2], x[1]), reverse=True)

    competition_group_green_stacks = {group_id: [] for group_id in filtered_competition_groups}

    for applicant_id in sorted(applicants, key=lambda x: applicants[x]['max_score_total'], reverse=True):
        if applicant_id in granted:
            continue
        if any([item[1] in mag_goal_to_common for item in applicants[applicant_id]['competition_groups_priorities']]):
            calculate_place(applicant_id, 0,
                            applicants, competition_group_green_stacks, filtered_competition_groups, logout)
    for group_id in mag_goal_to_common:
        if len(competition_group_green_stacks[group_id]) > 0:
            # print("Целевая", group_id, competition_group_green_stacks[group_id], file=logout)
            filtered_competition_groups[mag_goal_to_common[group_id]] -= len(competition_group_green_stacks[group_id])

    for group_id in competition_group_green_stacks:
        competition_group_green_stacks[group_id].clear()
    for applicant_id in sorted(applicants, key=lambda x: applicants[x]['max_score_total'], reverse=True):
        if applicant_id in granted:
            continue
        applicants[applicant_id]["consent"] = ""
        result = calculate_place(applicant_id, 0,
                                 applicants, competition_group_green_stacks, filtered_competition_groups, logout)

    check_green_stacks(competition_group_green_stacks, filtered_competition_groups, applicants, logout)

    return applicants, competition_group_green_stacks


def calculate_white_stacks(ratings, filtered_competition_groups, granted):
    white_stacks = {group_id: [] for group_id in filtered_competition_groups}

    applicants_json = {}
    for rating in ratings:
        group_id = rating["competition_group_id"]
        modified_total_score = int(rating["score_total"])
        if rating['applicant_id'] in granted:
            continue
        # if rating['note'] == "Без вступительных испытаний":
        #     modified_total_score = 500

        if group_id in white_stacks:
            """
            if int(rating["score_subject_1"]) == 0 or \
                    int(rating["score_subject_2"]) == 0 or \
                    int(rating["score_subject_3"]) == 0:
                print("Wrong score", rating['applicant_id'], int(rating["score_subject_1"]),
                      int(rating["score_subject_2"]), int(rating["score_subject_3"]))
            """
            white_stacks[group_id].append((
                int(rating["consent_submitted"]),
                (
                    modified_total_score,
                    int(rating["score_subject_1"]) + int(rating["score_subject_2"]) + int(rating["score_subject_3"]),
                    int(rating["score_subject_1"]),
                    int(rating["score_subject_2"]),
                    int(rating["score_subject_3"])
                ),
                int(rating['priority']) if rating['priority'] != "" else 0,
                int(rating["original_submitted"]),

                rating['applicant_id'],
                rating["note"].replace('&quot;', '"') + " " + rating["status"]
            ))
            if rating['applicant_id'] in applicants_json:
                applicants_json[rating['applicant_id']].append((
                    int(rating['priority']) if rating['priority'] != "" else 0,
                    group_id,
                    (
                        modified_total_score,
                        int(rating["score_subject_1"]) + int(rating["score_subject_2"]) + int(
                            rating["score_subject_3"]),
                        int(rating["score_subject_1"]),
                        int(rating["score_subject_2"]),
                        int(rating["score_subject_3"])
                    ),
                    rating["consent_submitted"],
                    rating["original_submitted"],
                    rating["note"].replace('&quot;', '"') + " " + rating["status"]
                ))
            else:
                applicants_json[rating['applicant_id']] = [(
                    int(rating['priority']) if rating['priority'] != "" else 0,
                    group_id,
                    (
                        modified_total_score,
                        int(rating["score_subject_1"]) + int(rating["score_subject_2"]) + int(
                            rating["score_subject_3"]),
                        int(rating["score_subject_1"]),
                        int(rating["score_subject_2"]),
                        int(rating["score_subject_3"])
                    ),
                    rating["consent_submitted"],
                    rating["original_submitted"],
                    rating["note"].replace('&quot;', '"') + " " + rating["status"]
                )]

            """ modified_priority, group_id, scoring(5*int), consent, original, note """

    for group_id in white_stacks:
        white_stacks[group_id].sort(reverse=True, key=lambda x: (x[0], x[1], -x[2], x[3]))
    for applicant_id in applicants_json:
        applicants_json[applicant_id].sort()

    return white_stacks, applicants_json


def print_out(datenow, competition_groups, competition_group_green_stacks, filtered_competition_groups,
              competition_group_white_stacks):
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
                f"План {filtered_competition_groups[group_id]} мест, "
                f"текущая заполненность {len(competition_group_green_stacks[group_id])}",
                file=outfile)
            for i in range(len(competition_group_green_stacks[group_id])):
                print(
                    f"{i + 1}. {competition_group_green_stacks[group_id][i][1]}, "
                    f"{competition_group_green_stacks[group_id][i][0][0]} баллов "
                    f"{competition_group_green_stacks[group_id][i][0][2], competition_group_green_stacks[group_id][i][0][3], competition_group_green_stacks[group_id][i][0][4]}",
                    file=outfile)
            print("-" * 20, file=outfile)

    with open('result_data/' + datenow + "_brief.csv", 'w', encoding="utf-8") as outfile:
        print("specialty_code", "profile", "institution_name", "education_form", "funding", "category",
              'plan_places', "current_places", "fraction", "ratings", "originals", sep=';', file=outfile)
        for group_id in competition_group_green_stacks:
            print("'"+competition_groups[group_id]["specialty_code"],
                  competition_groups[group_id]["profile"],
                  competition_groups[group_id]["institution_name"],
                  competition_groups[group_id]["education_form"],
                  competition_groups[group_id]["funding"],
                  competition_groups[group_id]["category"],
                  filtered_competition_groups[group_id],
                  len(competition_group_green_stacks[group_id]),
                  0 if filtered_competition_groups[group_id] == 0
                  else len(competition_group_green_stacks[group_id]) / filtered_competition_groups[group_id],
                  len(competition_group_white_stacks[group_id]),
                  sum([item[3] for item in competition_group_white_stacks[group_id]]),
                  sep=';', file=outfile)




if __name__ == "__main__":
    logout = sys.stdout
    main_parsing(logout)
