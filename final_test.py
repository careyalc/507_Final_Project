import unittest
from final import *

#do i have to test my cache???

class TestCrawling(unittest.TestCase):

	def test_umma_crawl(self):
		try:
			get_umma_titles("apple")
			get_umma_titles("dinner")
			get_umma_titles("lemon")
			get_umma_titles("mandolin")
		except:
			self.fail()

	def test_result_crawl(self):
		output = get_umma_titles("apple")
		self.assertEqual(type(output), list) #is this correct???
		for each in output:
			self.assertIn('resources', output)
			self.assertIn('view', output)



class TestDatabase(unittest.TestCase):

	# def test_existence(self):
	# 	output = create_art_db()
	# 	self.assertNotEqual(output, "Sorry, cannot create database")

	def test_art_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        crawl_and_populate(get_umma_titles("apple"))
        #add another test word later? in same function?

        statement = 'SELECT Title FROM Art'
        results = cur.execute(statement)
        result_list = results.fetchall()
        self.assertIn(('Still Life with Apples',), result_list)
        self.assertEqual(len(result_list), 12)
        self.assertEqual(result_list[1], "Apples")
        conn.close()

    def test_artist_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        populate_art_table(crawl_and_populate(get_umma_titles("apple")))

        statement = 'SELECT LastName FROM Artists'
        results = cur.execute(statement)
        result_list = results.fetchall()
        self.assertIn(('Freckelton',), result_list)
        self.assertEqual(len(result_list), 12)
        self.assertEqual(result_list[1], "Sears")
        conn.close()

    def test_joins(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        populate_art_table(crawl_and_populate(get_umma_titles("apple")))

        statement = "SELECT Title FROM Art JOIN Artists ON Art.ArtistId = Artists.Id WHERE LastName = 'Raimondi' "
        results = cur.execute(statement)
        result = results.fetchone()
        self.assertEqual(('Serpent Speaking to a Young Man',), result)
        conn.close()


class TestClass(unittest.TestCase):

	def test_constructor(self):
		picasso = Art("The Bull Fight", "Pablo Picasso", "Van Gogh", "1934", "oil on canvas", "17 3/8 in. x 22 11/16 in. x 1 15/16 in. ", "https://exchange.umma.umich.edu/resources/12175/view")
		self.assertEqual(picasso.artist_last_name, "Picasso")
		self.assertEqual(picasso.title, "The Bull Fight")
		self.assertEqual(picasso.medium, "oil on canvas")
		self.assertEqual(picasso.url, "https://exchange.umma.umich.edu/resources/12175/view")

		mann = Art("Larry's Kiss", "Sally Mann", "Mann", "1992", "gelatin silver print on paper", "8 in x 10 in", "https://exchange.umma.umich.edu/resources/9174/view")
		self.assertEqual(mann.artist, "Sally Mann")
		self.assertEqual(mann.title, "Larry's Kiss")
		self.assertEqual(mann.date, "1992")
		self.assertEqual(mann.dim, "8 in x 10 in")



class TestPlotting(unittest.TestCase):

    # can't test to see if the maps are correct, but can test that the functions don't return an error
    def test_bar_chart(self):
    	output1 = crawl_and_populate(get_umma_titles("apple"))
		populate_art_table(output1)

		output2 = crawl_and_populate(get_umma_titles("dinner"))
		populate_art_table(output2)

        try:
            plot_artists_for_search(output1)
            plot_artists_for_search(output2)
        except:
            self.fail()

    def test_pie_chart(self):
    	populate_art_table(crawl_and_populate(get_umma_titles("apple")))

		try:
            plot_medium()
        except:
            self.fail()

		populate_art_table(crawl_and_populate(get_umma_titles("dinner")))

        try:
            plot_medium()
        except:
            self.fail()


class TestInteractive(unittest.TestCase):

    def test_interactive_prompt(self):
        results = process_command('bars ratings top=1')
        self.assertEqual(results[0][0], 'Chuao')

       



if __name__ == '__main__':
    unittest.main()