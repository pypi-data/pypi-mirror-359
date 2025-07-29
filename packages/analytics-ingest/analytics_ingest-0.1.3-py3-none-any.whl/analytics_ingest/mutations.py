class GraphQLMutations:
    @staticmethod
    def create_configuration():
        return """
            mutation createConfiguration($input: CreateConfigurationInput!) {
                createConfiguration(input: $input) {
                    id
                    deviceId
                    vehicleId
                    organizationId
                    fleetId
                }
            }
        """

    @staticmethod
    def create_message():
        return """
            mutation createMessage($input: CreateMessageInput!) {
                createMessage(input: $input) {
                    id
                    arbId
                    name
                    networkName
                    ecuId
                    ecuName
                    fileId
                }
            }
        """

    @staticmethod
    def upsert_signal_data():
        return """
            mutation UpsertSignalData($input: UpsertSignalDataInput) {
                upsertSignalData(input: $input) {
                    configurationId
                    messageId
                    messageName
                    name
                    paramType
                    unit
                }
            }
        """
