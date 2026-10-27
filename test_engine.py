import unittest
from engine import details, calculate, vimshottari_birth_balance

class CalculatorTests(unittest.TestCase):
    def test_rasi_d9_starts(self):
        self.assertEqual(details(0)['navamsa_sign'],'Aries')
        self.assertEqual(details(30)['navamsa_sign'],'Capricorn')
        self.assertEqual(details(60)['navamsa_sign'],'Libra')
        self.assertEqual(details(90)['navamsa_sign'],'Cancer')
    def test_pada_edges(self):
        self.assertEqual(details(0)['pada'],1)
        self.assertEqual(details(10)['pada'],4)
        self.assertEqual(details(13+1/3)['nakshatra'],'Bharani')
    def test_calculation(self):
        r=calculate({'date':'1993-01-31','time':'21:45','latitude':12.9716,'longitude':77.5946,'timezone':'Asia/Kolkata','ayanamsa':'lahiri'})
        self.assertEqual(r['ascendant']['sign'],'Virgo')
        self.assertEqual(len(r['planets']),12)
        self.assertAlmostEqual((r['planets']['Ketu']['longitude']-r['planets']['Rahu']['longitude'])%360,180,places=6)
    def test_sundar_chennai_reference_inputs(self):
        r=calculate({'date':'1973-09-29','time':'21:00','latitude':13.0827,'longitude':80.2707,'timezone':'Asia/Kolkata','ayanamsa':'lahiri','node':'mean'})
        self.assertEqual(r['utc'], '1973-09-29T15:30:00+00:00')
        self.assertEqual(r['ascendant']['sign'],'Taurus')
        self.assertEqual(r['planets']['Sun']['sign'],'Virgo')
        self.assertEqual(r['planets']['Moon']['sign'],'Libra')
        self.assertEqual(r['planets']['Jupiter']['sign'],'Capricorn')
    def test_keerthi_v_madugula_reference(self):
        r=calculate({'name':'Keerthi Chennuru','date':'1984-07-06','time':'02:40',
                     'latitude':17.9078,'longitude':82.8098,'timezone':'Asia/Kolkata',
                     'ayanamsa':'lahiri','node':'mean'})
        self.assertEqual(r['utc'], '1984-07-05T21:10:00+00:00')
        self.assertEqual(r['ascendant']['sign'],'Taurus')
        for planet,sign in {'Sun':'Gemini','Moon':'Virgo','Mars':'Libra',
                 'Mercury':'Cancer','Jupiter':'Sagittarius','Venus':'Gemini',
                 'Saturn':'Libra','Rahu':'Taurus','Ketu':'Scorpio'}.items():
            self.assertEqual(r['planets'][planet]['sign'],sign)
        self.assertEqual(r['planets']['Moon']['nakshatra'],'Hasta')
        self.assertEqual(r['planets']['Moon']['pada'],4)
        self.assertEqual(r['planets']['Moon']['navamsa_sign'],'Cancer')
        b=r['birth_dasha_balance']
        self.assertEqual((b['lord'],b['years'],b['months'],b['days']),('Moon',2,2,9))
    def test_hasta_pada_boundary(self):
        self.assertEqual(details(150+19.99999)['pada'],3)
        self.assertEqual(details(150+20.00001)['pada'],4)
    def test_kishore_prasad_1978_windows_pre_epoch_dasha(self):
        r=calculate({'name':'Kishore Prasad','date':'1978-08-15','time':'22:45',
                     'place':'Krishnagiri, Tamil Nadu, India',
                     'latitude':12.519,'longitude':78.213,'timezone':'Asia/Kolkata',
                     'ayanamsa':'lahiri','node':'mean'})
        self.assertEqual(r['utc'],'1978-08-15T17:15:00+00:00')
        self.assertEqual(r['ascendant']['sign'],'Aries')
        self.assertTrue(any(int(p['start'][:4])<1970 for p in r['vimshottari']['periods']))
        self.assertTrue(all(len(p['children'])==9 for p in r['vimshottari']['periods']))
    def test_historical_1945_birth_date(self):
        r=calculate({'date':'1945-08-15','time':'22:45',
                     'latitude':12.519,'longitude':78.213,'timezone':'Asia/Kolkata'})
        self.assertTrue(r['vimshottari']['periods'])
    def test_timezone_required(self):
        with self.assertRaises(Exception): calculate({'date':'1993-01-31','time':'21:45','latitude':13,'longitude':80,'timezone':'Bad/Timezone'})


class DashaRegressionTests(unittest.TestCase):
    def test_keerthi_mindsutra_major_and_rahu_bhukti(self):
        r=calculate({'date':'1984-07-06','time':'02:40', 'latitude':17.9078,'longitude':82.8098,'timezone':'Asia/Kolkata','ayanamsa':'lahiri','node':'mean'})
        j=next(p for p in r['vimshottari']['periods'] if p['lord']=='Jupiter')
        self.assertEqual((j['start'],j['end']),('2011-09-14','2027-09-14'))
        rahu=next(x for x in j['children'] if x['lord']=='Rahu')
        self.assertEqual((rahu['start'],rahu['end']),('2025-04-21','2027-09-14'))
        self.assertEqual(len(rahu['children']),9)
    def test_no_gaps_jupiter_bhuktis(self):
        r=calculate({'date':'1984-07-06','time':'02:40', 'latitude':17.9078,'longitude':82.8098,'timezone':'Asia/Kolkata'})
        for period in r['vimshottari']['periods']:
            items=period['children']
            self.assertAlmostEqual(items[0]['start_jd'],period['start_jd'],places=7)
            self.assertAlmostEqual(items[-1]['end_jd'],period['end_jd'],places=7)
            for a,b in zip(items,items[1:]):self.assertAlmostEqual(a['end_jd'],b['start_jd'],places=7)

if __name__=='__main__': unittest.main()
