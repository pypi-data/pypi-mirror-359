from cubicweb.devtools import BASE_URL
from cubicweb.devtools.testlib import MAILBOX
from cubicweb_web.devtools.testlib import WebCWTC


class CommentViewsTC(WebCWTC):
    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            self.set_option("default-dest-addrs", "john.doe@example.com")
            self.blogentry = cnx.create_entity(
                "BlogEntry", title="une news !", content="cubicweb c'est beau"
            )
            cnx.commit()

    def test_notif_after_add_relation_comments(self):
        with self.admin_access.web_request() as req:
            comment = req.create_entity("Comment", content="Yo !")
            req.execute(
                f"SET C comments B WHERE B eid {self.blogentry.eid}, C eid"
                f" {comment.eid}"
            )
            self.assertEqual(len(MAILBOX), 0)
            req.cnx.commit()
            self.assertEqual(len(MAILBOX), 1)
            email = MAILBOX[0]
            self.assertEqual(email.subject, "new comment for BlogEntry une news !")
            self.assertMultiLineEqual(
                email.content,
                f"""Yo !


i18n_by_author_field: admin
url: {BASE_URL}blogentry/%s"""
                % self.blogentry.eid,
            )


if __name__ == "__main__":
    import unittest

    unittest.main()
