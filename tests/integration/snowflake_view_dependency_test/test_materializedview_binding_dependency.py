from tests.integration.base import DBTIntegrationTest, use_profile

class TestSnowflakeLateBindingMaterializedViewDependency(DBTIntegrationTest):

    @property
    def schema(self):
        return "snowflake_view_dependency_test"

    @property
    def models(self):
        return "models"

    @property
    def project_config(self):
        return {
            'config-version': 2,
            'seed-paths': ['seeds'],
            'seeds': {
                'quote_columns': False,
            },
            'quoting': {
                'schema': False,
                'identifier': False
            }
        }

    """
    Snowflake views are not bound to the relations they select from. A Snowflake view
    can have entirely invalid SQL if, for example, the table it selects from is dropped
    and recreated with a different schema. In these scenarios, Snowflake will raise an error if:
    1) The view is queried
    2) The view is altered

    dbt's logic should avoid running these types of queries against views in situations
    where they _may_ have invalid definitions. These tests assert that views are handled
    correctly in various different scenarios
    """

    @use_profile('snowflake')
    def test__snowflake__changed_table_schema_for_downstream_view(self):
        results = self.run_dbt(["seed"])
        self.assertEqual(len(results),  1)

        results = self.run_dbt(["run", "--vars", "{dependent_type: materializedview}"])
        self.assertEqual(len(results),  2)
        self.assertManyTablesEqual(["PEOPLE", "BASE_TABLE", "DEPENDENT_MODEL"])

        # Change the schema of base_table, assert that dependent_model doesn't fail
        results = self.run_dbt(["run", "--vars", "{add_table_field: true, dependent_type: materializedview}"])
        self.assertEqual(len(results),  2)
        self.assertManyTablesEqual(["BASE_TABLE", "DEPENDENT_MODEL"])

