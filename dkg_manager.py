from neo4j import GraphDatabase

class DKGManager:
    """Manages the connection and interactions with the event-driven Knowledge Graph."""

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def run_query(self, query, parameters=None):
        """Runs a read-only Cypher query and returns the results."""
        with self._driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

    def add_event_to_chain(self, chain_id, event_props):
        """Adds a new event to a workflow chain, linking it to the previous event."""
        with self._driver.session() as session:
            # This complex transaction finds the last event in the chain and links the new one.
            session.write_transaction(self._create_and_link_event, chain_id, event_props)

    @staticmethod
    def _create_and_link_event(tx, chain_id, event_props):
        # Find the chain's anchor node (e.g., the Ticket itself)
        tx.run("MERGE (c:Chain {id: $chain_id})", chain_id=chain_id)
        
        # Find the last event in this chain
        last_event_query = """
        MATCH (c:Chain {id: $chain_id})
        OPTIONAL MATCH (c)-[:HAS_EVENT]->(e:Event)
        WITH e ORDER BY e.timestamp DESC LIMIT 1
        RETURN e
        """
        result = tx.run(last_event_query, chain_id=chain_id)
        last_event_node = result.single()

        # Create the new event
        new_event_query = """
        CREATE (newEvent:Event $props)
        RETURN newEvent
        """
        new_event_result = tx.run(new_event_query, props=event_props)
        new_event_node = new_event_result.single()[0]

        # Link the new event
        if last_event_node and last_event_node[0]:
            # Link to the previous event
            link_query = """
            MATCH (prev:Event {id: $prev_id}), (new:Event {id: $new_id})
            MERGE (prev)-[:NEXT]->(new)
            """
            tx.run(link_query, prev_id=last_event_node[0]['id'], new_id=new_event_node['id'])
        else:
            # This is the first event, link it to the main chain anchor
            link_query = """
            MATCH (c:Chain {id: $chain_id}), (e:Event {id: $event_id})
            MERGE (c)-[:HAS_EVENT]->(e)
            """
            tx.run(link_query, chain_id=chain_id, event_id=new_event_node['id'])