import sys
import requests
import json


class CloudendureSDK:
    def __init__(self, userApiToken: str):
        self.host = 'https://console.cloudendure.com'
        self.endpoint = '/api/latest/{}'
        self.session = self.login(userApiToken)

    # Authentication API
    def login(self, userApiToken: str):
        '''
        Upon successful authentication, this method returns a session identifier cookie that can be used to authenticate subsequent API calls.
        :param userApiToken:
        :return:
        '''
        session = requests.Session()
        session.headers.update({'Content-type': 'application/json', 'Accept': 'text/plain'})
        response = session.post(url=self.host + self.endpoint.format('login'),
                                data=json.dumps({'userApiToken': userApiToken}))
        # Report any login errors
        if response.status_code != 200 and response.status_code != 307:
            print('Could not login!')
            print(response.reason)
            print(response.request.body)
            sys.exit(2)
        if session.cookies.get('XSRF-TOKEN'):
            session.headers['X-XSRF-TOKEN'] = session.cookies.get('XSRF-TOKEN')
        return session

    def logout(self):
        '''
        Invalidates the session identifier associated with this session.
        :return:
        '''
        response = self.session.get(url=self.host + self.endpoint.format('logout'))
        return response

    # Blueprint API
    def get_blueprint(self, projectId: str, blueprintId: str):
        """Returns a blueprint from a project.

        Returns:
            [dict] : blueprint
        """
        response = self.session.get(url=self.host + self.endpoint.format(
            'projects/{}/blueprints/{}'.format(projectId, blueprintId))).json()
        return response

    def list_blueprint(self, projectId: str):
        '''
        Returns the list of available blueprints in the project.
            NOTE: Not compatible with Default Project
        :param projectId:
        :return:
        '''
        response = self.session.get(url=self.host + self.endpoint.format(
            'projects/{}/blueprints'.format(projectId))).json()['items']
        for bp in response:
            bp.update({"projectId": projectId})
        return response

    def configure_blueprint(self, projectId: str, blueprintId: str, blueprint):
        """Configure target machine characteristics: machine and disk types, network configuration, etc. Returns the
        modified object.

        Returns:
            [dict] : blueprint
        """
        response = (self.session.patch(
            url=self.host + self.endpoint.format('projects/{}/blueprints/{}'.format(projectId, blueprintId)),
            json=blueprint))

        return response

    # Machine API
    def get_machine(self, projectId: str, machineId: str):
        '''
        Get a specific machine
        :param projectId:
        :param machineId:
        :return:
        '''
        response = self.session.get(url=self.host + self.endpoint.format(
            'projects/{}/machines/{}'.format(projectId, machineId))).json()
        return response

    def list_machines(self, projectId: str, showAll=True, limit=1500, offset=0):
        '''
        Returns the list of all source machines in the Project (i.e. machines that have an Agent installed).
        :param projectId:
        :param showAll:
        :param limit:
        :param offset:
        :return:
        '''
        query_params = {
            'all': showAll,
            'limit': limit,
            'offset': offset
        }
        response = self.session.get(url=self.host + self.endpoint.format(
            'projects/{}/machines'.format(projectId)), params=query_params).json()['items']
        return response

    def uninstall_agent(self, projectId: str, machineId: str):
        '''
        Stops replication and removes the cloudendure2 agent from this machine. All cloud artifacts associated with those machines with the exception of launched target machine are deleted.
        :param projectId:
        :param machineId:
        :return:
        '''
        response = self.session.delete(url=self.host + self.endpoint.format(
            'projects/{}/machines/{}'.format(projectId, machineId))).json()
        return response

    def get_target_machine(self, projectId: str, replicaId: str):
        '''

        :param projectId:
        :param replicaId:
        :return:
        '''
        response = self.session.delete(url=self.host + self.endpoint.format(
            'projects/{}/replicas/{}'.format(projectId, replicaId))).json()
        return response

    def uninstall_multiple_agents(self, projectId: str, machineIDs: list):
        '''
        Stops replication and removes the cloudendure2 agent from the specified machines. All cloud artifacts associated
        with those machines with the exception of launched target machines are deleted.
        :param projectId:
        :param machineIDs:
        :return:
        '''
        response = self.session.delete(url=self.host + self.endpoint.format(
            'projects/{}/machines'.format(projectId)), json=machineIDs ).json()
        return response

    # Project API
    def get_project(self, projectId):
        '''

        :param projectId:
        :return:
        '''
        response = (self.session.get(url=self.host + self.endpoint.format('projects/{}'.format(projectId)))).json()
        return response

    def list_projects(self):
        '''
        Returns the list of projects defined in this account.
        :return:
        '''
        response = (self.session.get(url=self.host + self.endpoint.format('projects'))).json()['items']
        return response

    # Replication API
    def list_replication_configurations(self, projectId):
        """Returns the list of replication configuration objects defined in this project.

        Returns:
            list
        """
        response = self.session.get(
            url=self.host + self.endpoint.format('projects/{}/replicationConfigurations'.format(projectId))).json()[
            'items']
        for bp in response:
            bp.update({"projectId": projectId})
        return response

    def list_available_pit(self, projectId: str, machineId: str):
        response = (self.session.get(url=self.host + self.endpoint.format(
            'projects/{}/machines/{}/pointsintime'.format(projectId, machineId)))).json()['items']
        return response

    # Recovery Plan API
    def get_recovery_plan(self, projectId: str, recoveryPlanId: str):
        response = (self.session.get(url=self.host + self.endpoint.format(
            'projects/{}/recoveryPlans/{}'.format(projectId, recoveryPlanId)))).json()['items']
        return response

    def updates_recovery_plan(self, projectId: str, recoveryPlanId: str, steps):
        ce_steps = self.get_recovery_plan(projectId=projectId, recoveryPlanId=recoveryPlanId)
        ce_steps.update(steps)
        response = (self.session.patch(
            url=self.host + self.endpoint.format('projects/{}/recoveryPlans/{}'.format(projectId, recoveryPlanId)),
            json=ce_steps))
        return response

    def delete_recovery_plan(self, projectId: str, recoveryPlanId: str):
        response = self.session.delete(url=self.host + self.endpoint.format(
            'projects/{}/recoveryPlans/{}'.format(projectId, recoveryPlanId))).json()
        return response
