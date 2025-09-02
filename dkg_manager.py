from neo4j import GraphDatabase

class DKGManager:
    """Manages the connection and all interactions with the Neo4j Decision Knowledge Graph."""

    def __init__(self, uri, user, password):
        # Establishes the connection to the database.
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Closes the database connection.
        self._driver.close()

    def _execute_write(self, tx, query, parameters=None):
        # Helper function to run a write transaction.
        tx.run(query, parameters)

    def add_node(self, label, properties):
        """
        Adds or updates a node in the graph, ensuring no duplicates based on a unique 'id' property.
        """
        # A node's unique ID is its most specific identifier (email for User, id for Ticket, etc.)
        # This ensures we don't create duplicate nodes for the same entity.
        unique_id = properties.get('id') or properties.get('email') or properties.get('term')
        if not unique_id:
            raise ValueError("Node properties must contain a unique identifier ('id', 'email', or 'term')")
        
        properties['id'] = unique_id

        query = f"MERGE (n:{label} {{id: $id}}) SET n = $props RETURN n"
        
        with self._driver.session() as session:
            session.write_transaction(self._execute_write, query, parameters={'id': unique_id, 'props': properties})

    def add_relationship(self, start_node_label, start_node_id, end_node_label, end_node_id, rel_type, rel_props=None):
        """Adds a relationship between two existing nodes."""
        rel_props = rel_props or {}
        query = (
            f"MATCH (a:{start_node_label} {{id: $start_id}}), (b:{end_node_label} {{id: $end_id}}) "
            f"MERGE (a)-[r:{rel_type}]->(b) "
            f"SET r += $props"
        )
        with self._driver.session() as session:
            session.write_transaction(self._execute_write, query, parameters={
                'start_id': start_node_id,
                'end_id': end_node_id,
                'props': rel_props
            })