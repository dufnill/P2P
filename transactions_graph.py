import logging
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

class App:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def create_transaciton(self, id, block_num):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._create_and_return_transaction, id, block_num)
            for record in result:
                print("Created transaction {id} in block {block_num}".format(
                    id=record['id'], block_num=record['block_num']))

    @staticmethod
    def _create_and_return_transaction(tx, id, block_num):
        
        #query and its execution
        query = (
            "CREATE (t:Trx { id: $id, block_num: $block_num }) "
            "RETURN t"
        )
        result = tx.run(query, id=id, block_num=block_num)

        #printing result
        try:
            return [{"t": record["t"]["id"]} for record in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def find_transaction(self, id):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_and_return_person, id)
            for record in result:
                print("Found person: {record}".format(record=record))

    @staticmethod
    def _find_and_return_transaction(tx, id):
        query = (
            "MATCH (t:Trx) "
            "WHERE t.id = $id "
            "RETURN t.id AS id"
        )
        result = tx.run(query, id=id)
        return [record["id"] for record in result]

if __name__ == "__main__":
    # See https://neo4j.com/developer/aura-connect-driver/ for Aura specific connection URL.
    scheme = "neo4j"  # Connecting to Aura, use the "neo4j+s" URI scheme
    host_name = "example.com"
    port = 7687
    url = "{scheme}://{host_name}:{port}".format(scheme=scheme, host_name=host_name, port=port)
    user = "davide"
    password = "password"
    app = App(url, user, password)
    app.create_transaciton("1", "1")
    app.find_transaction("1")
    app.close()