import unittest
from cubicweb.devtools.testlib import CubicWebTC


class PersonTC(CubicWebTC):
    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.create_entity('Person', firstname=u'adrien', surname=u'di mascio')
            cnx.commit()

    def test_dc_title(self):
        with self.admin_access.client_cnx() as cnx:
            e = cnx.execute('Any X WHERE X is Person').get_entity(0, 0)
            self.assertEqual(e.dc_title(), 'adrien di mascio')
            self.assertEqual(e.dc_long_title(), 'Mr adrien di mascio')


if __name__ == '__main__':
    unittest.main()
