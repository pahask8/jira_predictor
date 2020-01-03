import json
import logging
import os

import yaml

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)

users_file = "users.yaml"

# read users
with open(users_file, 'r') as f:
    users = yaml.load(f, Loader=yaml.FullLoader)
    active_users = users['active']
    blocked_users = users['blocked']
    replacement_users = users['replacement']

ingnored_components_name = [
    "i'm not sure",
]


def read_from_jira_datasets(path: str) -> json:
    result = []
    files = os.listdir(path)
    for file_path in files:
        with open(os.path.join(path, file_path), 'r') as f:
            update = dict()

            ticket = json.loads(f.read())

            # ticket number
            update['number'] = ticket['key']

            # project
            update['project_name'] = ticket['fields']['project']['name']

            # components
            components = sorted(list(set([_['name'].lower() for _ in ticket['fields']['components'] if _ not in ingnored_components_name])))
            components_description = sorted(list(set([_['description'].lower() for _ in ticket['fields']['components'] if _.get('description')])))
            update['components_name'] = ", ".join(components)
            update['components_description'] = ", ".join(components_description)

            # description
            update['description'] = ticket['fields']['description']

            # summary
            update['summary'] = ticket['fields']['summary']

            # get a most active user
            comments = ticket['fields']['comment']['comments']

            ignored_comments = ['autoclose', 'closed as obsolete', 'bulk closing', 'due to inactivity']

            for idx, comment in enumerate(comments):
                for ignore in ignored_comments:
                    if ignore in comment['body'].lower():
                        comments[idx] = {}

            update['comments'] = " ".join([_.get('body') for _ in comments if _.get('body')])

            try:
                authors = [_['author']['key'] for _ in comments]
                authors_full_names = [_['author']['displayName'] for _ in comments]
            except KeyError:
                LOG.warning(f"There is no author in the ticket, ticket: {ticket}")
                continue

            users = list(set(authors) & set(active_users.keys()))  # get users only from the ticket
            if not users:
                # eplace_users = []
                # try to use mapping
                for user in list(set(authors)):
                    for replace_user, replace_data in replacement_users.items():
                        if user in replace_data:
                            LOG.info(f"Found a replacement user: {replace_user}, blocked user: {user}")
                            users.append(replace_user)
                        # else:
                        #     LOG.warning(f"The blocked user {user} not in the replacement data: {replace_data}, replacement user: {replace_user}")
                        #     print()

                # users = list(set(authors) & set(replace_users))
                if not users:
                    LOG.warning(f"There are no devops active users, authors_full_names: {authors_full_names}, authors: {authors}, file_path: {file_path}")
                    blocked_most_active_user = list(set(authors) & set(blocked_users.keys()))  # get blocked users only from the ticket
                    if blocked_most_active_user:
                        blocked_most_active_user = (max(set(blocked_most_active_user), key=users.count))
                        LOG.warning(f"The most active user has been blocked, user: {blocked_most_active_user}: {blocked_users[blocked_most_active_user]}, ticket: {ticket}")
                        print()
                    continue
            update['most_active_user_key'] = (max(set(users), key=users.count))
            update['most_active_user_display_name'] = active_users.get(update['most_active_user_key'], '')

            result.append(update)
    return result


dir_path = os.path.dirname(os.path.realpath(__file__))


def preprocess(result: list):
    """

    datasets:
        most_active_user_key
    """
    for ticket in result:
        active_user_dir = os.path.join(dir_path, "dataset_preprocess", ticket["most_active_user_key"])
        ticket_to_create_path = os.path.join(dir_path, "dataset_preprocess", active_user_dir, f"{ticket['number']}.txt")
        # create a folder if not exists
        if not os.path.exists(active_user_dir):
            os.makedirs(active_user_dir)

        description = ticket.get("description", "") if ticket.get("description") else ""
        summary = ticket.get("summary", "")
        components_name = ticket.get("components_name", "")
        project_name = ticket.get("project_name", "")
        comments = ticket.get('comments')

        text = (project_name + " " + components_name + " " + description + " " + summary + " " + comments).lower()

        with open(ticket_to_create_path, "w") as f:
            f.write(text)


if __name__ == '__main__':
    # read a jira dataset
    dataset_path = "dataset_full"
    result = read_from_jira_datasets(dataset_path)
    # run preprocessing
    preprocess(result)
