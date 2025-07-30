from analytics_ingest.internal.mutations import GraphQLMutations


class ConfigurationService:
    def __init__(self, executor):
        self.executor = executor

    def create(self, device_id, fleet_id, org_id, vehicle_id):
        from analytics_ingest.internal.schemas.configuration_input import (
            make_configuration_input,
        )

        return self.executor.execute(
            GraphQLMutations.create_configuration(),
            make_configuration_input(device_id, fleet_id, org_id, vehicle_id),
        )
