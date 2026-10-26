"""App-owned copy in isiZulu, Afrikaans, isiXhosa and Sesotho.

Rows: English | isiZulu | Afrikaans | isiXhosa | Sesotho.
Placeholders are preserved so names, amounts and API identifiers stay untouched.
"""

COPY = r"""
Create account|Dala i-akhawunti|Skep rekening|Yenza iakhawunti|Theha akhaonto
Log in|Ngena|Meld aan|Ngena|Kena
MONEY PLANNING FOR FREELANCERS|UKUHLELA IMALI KWABAZISEBENZAYO|GELDBEPLANNING VIR VRYSKUTTERS|UCWANGCISO LWEMALI LWABAZISEBENZELAYO|MORALO OA CHELETE BAKENG SA BA IKEMETSENG
Plan for the days\n|Hlelela izinsuku\n|Beplan vir die dae\n|Cwangcisela iintsuku\n|Rera matsatsi\n
between paydays|phakathi kwezinsuku zokuhola|tussen betaaldae|eziphakathi kweentsuku zokuhlawulwa|a pakeng tsa matsatsi a moputso
Manage irregular income, cover essential bills, and save towards your goals with a clearer plan.|Phatha imali engenayo ngezikhathi ezingafani, khokhela izidingo ezibalulekile, wongele imigomo yakho ngohlelo olucacile.|Bestuur wisselende inkomste, betaal noodsaaklike rekeninge en spaar vir jou doelwitte met 'n duideliker plan.|Lawula ingeniso engafiki rhoqo, uhlawule amatyala abalulekileyo, uze wongele iinjongo zakho ngesicwangciso esicacileyo.|Laola chelete e kenang ka linako tse sa tšoaneng, lefa litšenyehelo tsa bohlokoa, 'me u bolokele lipheo tsa hao ka moralo o hlakileng.
Your language preference is saved on this device.|Ulimi olukhethile lugcinwa kule divayisi.|Jou taalvoorkeur word op hierdie toestel gestoor.|Ulwimi olukhethileyo lugcinwa kwesi sixhobo.|Puo eo u e khethileng e bolokoa sesebelisoeng sena.
Language|Ulimi|Taal|Ulwimi|Puo
Name|Igama|Naam|Igama|Lebitso
Email|I-imeyili|E-pos|I-imeyile|Imeile
Password|Iphasiwedi|Wagwoord|Igama lokugqitha|Phasewete
At least {v0} characters|Okungenani izinhlamvu ezingu-{v0}|Minstens {v0} karakters|Ubuncinane oonobumba abayi-{v0}|Bonyane litlhaku tse {v0}
Create your account|Dala i-akhawunti yakho|Skep jou rekening|Yenza iakhawunti yakho|Theha akhaonto ea hao
Welcome back|Siyakwamukela futhi|Welkom terug|Wamkelekile kwakhona|Rea u amohela hape
Back|Emuva|Terug|Buyela emva|Morao
Already have an account? Log in|Usunayo i-akhawunti? Ngena|Het jy reeds 'n rekening? Meld aan|Sele unayo iakhawunti? Ngena|U se u na le akhaonto? Kena
New here? Create an account|Umusha lapha? Dala i-akhawunti|Nuut hier? Skep 'n rekening|Umtsha apha? Yenza iakhawunti|U mocha mona? Theha akhaonto
Enter your name.|Faka igama lakho.|Voer jou naam in.|Faka igama lakho.|Kenya lebitso la hao.
Enter a valid email address.|Faka ikheli le-imeyili elivumelekile.|Voer 'n geldige e-posadres in.|Faka idilesi ye-imeyile esebenzayo.|Kenya aterese ea imeile e nepahetseng.
Enter your password.|Faka iphasiwedi yakho.|Voer jou wagwoord in.|Faka igama lakho lokugqitha.|Kenya phasewete ea hao.
Use at least {v0} characters.|Sebenzisa okungenani izinhlamvu ezingu-{v0}.|Gebruik minstens {v0} karakters.|Sebenzisa ubuncinane oonobumba abayi-{v0}.|Sebelisa bonyane litlhaku tse {v0}.
Password must be at least {v0} characters.|Iphasiwedi kufanele ibe nezinhlamvu okungenani ezingu-{v0}.|Die wagwoord moet minstens {v0} karakters bevat.|Igama lokugqitha kufuneka libe noonobumba abayi-{v0} ubuncinane.|Phasewete e tlameha ho ba le bonyane litlhaku tse {v0}.
Creating account|Sakha i-akhawunti|Rekening word geskep|Senza iakhawunti|Ho thehoa akhaonto
Signing in|Siyakungenisa|Besig om aan te meld|Uyangena|Ua kena
Signing out|Siyakukhipha|Besig om af te meld|Uyaphuma|Ua tsoa
Overview|Ukubuka konke|Oorsig|Isishwankathelo|Kakaretso
Cash flow|Ukuhamba kwemali|Kontantvloei|Ukuhamba kwemali|Phallo ea chelete
Transactions|Ukuthengiselana|Transaksies|Iintengiselwano|Litšebelisano
Goals|Imigomo|Doelwitte|Iinjongo|Lipheo
Profile|Iphrofayela|Profiel|Iprofayile|Boitsebiso
Open profile|Vula iphrofayela|Maak profiel oop|Vula iprofayile|Bula boitsebiso
Your profile|Iphrofayela yakho|Jou profiel|Iprofayile yakho|Boitsebiso ba hao
Plan currency|Uhlobo lwemali yohlelo|Plan se geldeenheid|Imali yesicwangciso|Mofuta oa chelete oa moralo
Sign out|Phuma|Meld af|Phuma|Tsoa
Refresh|Vuselela|Verfris|Hlaziya|Nchafatsa
Good morning|Sawubona ekuseni|Goeiemôre|Molo kusasa|Lumela hoseng
Good afternoon|Sawubona ntambama|Goeiemiddag|Molo emva kwemini|Lumela thapama
Good evening|Sawubona kusihlwa|Goeienaand|Molo ngokuhlwa|Lumela mantsiboea
A clear view of your plan before {v0}.|Uhlelo lwakho lucacile ngaphambi kuka-{v0}.|'n Duidelike blik op jou plan voor {v0}.|Isicwangciso sakho sicacile phambi ko-{v0}.|Pono e hlakileng ea moralo oa hao pele ho {v0}.
A clearer picture starts with your next expected payment.|Qala ngokufaka inkokhelo yakho elandelayo oyilindele.|'n Duideliker prentjie begin by jou volgende verwagte betaling.|Umfanekiso ocacileyo uqala ngentlawulo elandelayo oyilindeleyo.|Pono e hlakileng e qala ka tefo e latelang eo u e lebelletseng.
+ Add transaction|+ Engeza ukuthengiselana|+ Voeg transaksie by|+ Faka intengiselwano|+ Kenya tšebelisano
+ Add goal|+ Engeza umgomo|+ Voeg doelwit by|+ Faka injongo|+ Kenya sepheo
+ Add event|+ Engeza isehlakalo|+ Voeg gebeurtenis by|+ Faka isiganeko|+ Kenya ketsahalo
Available now|Okutholakala manje|Nou beskikbaar|Ekhoyo ngoku|E fumanehang hona joale
Confirmed money you can use today|Imali eqinisekisiwe ongayisebenzisa namuhla|Bevestigde geld wat jy vandag kan gebruik|Imali eqinisekisiweyo onokuyisebenzisa namhlanje|Chelete e netefalitsoeng eo u ka e sebelisang kajeno
Projected after planned events|Okulindelwe ngemva kokuhleliwe|Verwag ná beplande gebeure|Eqikelelweyo emva kweziganeko ezicwangcisiweyo|E hakantsoeng ka mor'a liketsahalo tse reriloeng
Estimate if expected income arrives|Isilinganiso uma imali oyilindele ifika|Raming indien verwagte inkomste ontvang word|Uqikelelo ukuba ingeniso elindelweyo iyafika|Khakanyo haeba chelete e lebelletsoeng e fihla
Projected from your latest update|Okulindelwe ngokwesibuyekezo sakho sakamuva|Verwag op grond van jou jongste opdatering|Uqikelelo olusekelwe kuhlaziyo lwakho lwamva|E hakantsoeng ho latela ntlafatso ea hao ea morao
PLANNED BALANCE|IBHALANSI EHLELIWE|BEPLANDE SALDO|IBHALANSI ECWANGCISIWEYO|CHELETE E SETSENG E RERILOENG
NEXT EXPECTED PAYMENT|INKOKHELO ELANDELAYO ELINDELEKILE|VOLGENDE VERWAGTE BETALING|INTLAWULO ELANDELAYO ELINDELWEYO|TEFO E LATELANG E LEBELLETSOENG
SAVINGS GOAL|UMGOMO WOKONGA|SPAARDOELWIT|INJONGO YOKONGA|SEPHEO SA POLOKO
View savings goals|Buka imigomo yokonga|Bekyk spaardoelwitte|Jonga iinjongo zokonga|Sheba lipheo tsa poloko
YOUR NEXT STEP|ISINYATHELO SAKHO ESILANDELAYO|JOU VOLGENDE STAP|INYATHELO LAKHO ELILANDELAYO|MOHATO OA HAO O LATELANG
Choose a savings goal|Khetha umgomo wokonga|Kies 'n spaardoelwit|Khetha injongo yokonga|Khetha sepheo sa poloko
Pick a target that matters to you. There is no required amount or schedule; progress follows what you record.|Khetha umgomo obalulekile kuwe. Alikho inani noma isikhathi esiyimpoqo; inqubekela phambili ilandela lokho okubhalayo.|Kies 'n doelwit wat vir jou saak maak. Daar is geen verpligte bedrag of skedule nie; vordering volg wat jy aanteken.|Khetha injongo ebalulekileyo kuwe. Akukho mali okanye xesha linyanzelekileyo; inkqubela ilandela oko ukubhalayo.|Khetha sepheo se bohlokoa ho uena. Ha ho chelete kapa nako e qobelloang; tsoelo-pele e latela seo u se tlalehang.
Create a goal|Dala umgomo|Skep 'n doelwit|Yenza injongo|Theha sepheo
Nothing to show yet|Akukho okuzoboniswa okwamanje|Nog niks om te wys nie|Akukho nto inokuboniswa okwangoku|Ha ho letho le ka bontšoang hajoale
Add an expected payment and a savings goal. Your forecast and progress build from what you enter.|Engeza inkokhelo oyilindele nomgomo wokonga. Isibikezelo nenqubekela phambili kusekelwe kulokho okufakayo.|Voeg 'n verwagte betaling en spaardoelwit by. Jou vooruitskatting en vordering word gebou op wat jy invoer.|Faka intlawulo oyilindeleyo nenjongo yokonga. Uqikelelo nenkqubela zisekelwe koko ukufakayo.|Kenya tefo eo u e lebelletseng le sepheo sa poloko. Khakanyo le tsoelo-pele li thehiloe ho seo u se kenyang.
Edit my plan|Hlela uhlelo lwami|Wysig my plan|Hlela isicwangciso sam|Fetola moralo oa ka
No planned events yet.|Azikho izehlakalo ezihleliwe okwamanje.|Nog geen beplande gebeure nie.|Akukho ziganeko zicwangcisiweyo okwangoku.|Ha ho liketsahalo tse reriloeng hajoale.
Latest planned balances from {v0} to {v1}, ending at {v2}.|Amabhalansi ahleliwe kusukela ku-{v0} kuya ku-{v1}, agcina ku-{v2}.|Jongste beplande saldo's van {v0} tot {v1}, wat op {v2} eindig.|Iibhalansi ezicwangcisiweyo ukusuka ku-{v0} ukuya ku-{v1}, ziphela ku-{v2}.|Chelete e setseng e reriloeng ho tloha ho {v0} ho ea ho {v1}, e qetella ho {v2}.
Cash-flow plan|Uhlelo lokuhamba kwemali|Kontantvloeiplan|Isicwangciso sokuhamba kwemali|Moralo oa phallo ea chelete
A chronological estimate — expected money is not guaranteed.|Isilinganiso ngokulandelana kwesikhathi — imali elindelekile ayiqinisekisiwe.|'n Raming volgens tyd — verwagte geld is nie gewaarborg nie.|Uqikelelo ngokulandelelana kwexesha — imali elindelweyo ayiqinisekiswanga.|Khakanyo ho latela nako — chelete e lebelletsoeng ha e tiisetsoe.
Until next payment|Kuze kube inkokhelo elandelayo|Tot die volgende betaling|Kude kufike intlawulo elandelayo|Ho fihlela tefo e latelang
Monthly|Nyanga zonke|Maandeliks|Rhoqo ngenyanga|Khoeli le khoeli
SELECTED PERIOD|ISIKHATHI ESIKHETHIWE|GEKOSE TYDPERK|IXESHA ELIKHETHIWEYO|NAKO E KHETHILOENG
Previous month|Inyanga edlule|Vorige maand|Inyanga edlulileyo|Khoeli e fetileng
Next month|Inyanga elandelayo|Volgende maand|Inyanga elandelayo|Khoeli e latelang
Nothing planned in this period yet.|Akukho okuhleliwe ngalesi sikhathi okwamanje.|Nog niks vir hierdie tydperk beplan nie.|Akukho nto icwangcisiweyo kweli xesha okwangoku.|Ha ho letho le reriloeng nakong ena hajoale.
Add an event to see how your balance moves.|Engeza isehlakalo ubone ukuthi ibhalansi yakho ishintsha kanjani.|Voeg 'n gebeurtenis by om te sien hoe jou saldo verander.|Faka isiganeko ukuze ubone indlela ibhalansi yakho etshintsha ngayo.|Kenya ketsahalo ho bona hore na chelete ea hao e setseng e fetoha joang.
Starting balance|Ibhalansi yokuqala|Beginsaldo|Ibhalansi yokuqala|Chelete e setseng qalong
Projected end balance|Ibhalansi yokugcina elindelekile|Verwagte eindsaldo|Ibhalansi yokugqibela eqikelelweyo|Chelete e setseng qetellong e hakantsoeng
Includes {v0} expected, not received.|Kufaka {v0} okulindelekile, okungakatholwa.|Sluit {v0} in wat verwag word, maar nog nie ontvang is nie.|Iquka {v0} elindelweyo, engekafunyanwa.|E kenyelletsa {v0} e lebelletsoeng, e so fumanoe.
Only money already received or paid is included.|Kufakwe kuphela imali esitholiwe noma esikhokhiwe.|Slegs geld wat reeds ontvang of betaal is, word ingesluit.|Kuqukwa kuphela imali esele ifunyenwe okanye ihlawulwe.|Ho kenyellelitsoe feela chelete e seng e fumanoe kapa e lefiloe.
Planned savings: {v0}. This is not an automatic transfer.|Imali ehlelelwe ukongiwa: {v0}. Lokhu akukudluliseli imali ngokuzenzakalela.|Beplande spaargeld: {v0}. Dit is nie 'n outomatiese oorplasing nie.|Imali ecwangciselwe ukongiwa: {v0}. Olu asilodluliselo oluzenzekelayo.|Poloko e reriloeng: {v0}. Ena ha se phetiso e iketsang.
Planned savings: R 0. This is not an automatic transfer.|Imali ehlelelwe ukongiwa: R 0. Lokhu akukudluliseli imali ngokuzenzakalela.|Beplande spaargeld: R 0. Dit is nie 'n outomatiese oorplasing nie.|Imali ecwangciselwe ukongiwa: R 0. Olu asilodluliselo oluzenzekelayo.|Poloko e reriloeng: R 0. Ena ha se phetiso e iketsang.
Expected|Okulindelekile|Verwag|Okulindelweyo|E lebelletsoeng
Upcoming|Okuzayo|Komend|Okuzayo|E tlang
Planned|Okuhleliwe|Beplan|Okucwangcisiweyo|E reriloeng
Planned, not transferred|Kuhleliwe, akukadluliselwa|Beplan, nie oorgeplaas nie|Kucwangcisiwe, akukadluliselwa|E reriloeng, e sa fetisoa
Received|Kutholiwe|Ontvang|Ifunyenwe|E fumanoeng
Paid|Kukhokhiwe|Betaal|Ihlawulwe|E lefiloeng
Expected income stays separate until it is received.|Imali elindelekile igcinwa yodwa ize itholwe.|Verwagte inkomste bly apart totdat dit ontvang word.|Ingeniso elindelweyo igcinwa yodwa ide ifunyanwe.|Chelete e lebelletsoeng e aroloa ho fihlela e fumanoa.
All|Konke|Alles|Konke|Tsohle
Income|Imali engenayo|Inkomste|Ingeniso|Chelete e kenang
Expenses|Izindleko|Uitgawes|Iindleko|Litšenyehelo
Expense|Izindleko|Uitgawe|Inkcitho|Tšenyehelo
From date (optional)|Kusukela osukwini (uyazikhethela)|Vanaf datum (opsioneel)|Ukususela kumhla (akunyanzelekanga)|Ho tloha ka letsatsi (boikhethelo)
No transactions in this month|Akukho ukuthengiselana kule nyanga|Geen transaksies hierdie maand nie|Akukho ntengiselwano kule nyanga|Ha ho litšebelisano khoeling ena
Add one to see how it affects your balance.|Engeza okukodwa ubone umphumela kubhalansi yakho.|Voeg een by om te sien hoe dit jou saldo beïnvloed.|Faka enye ukuze ubone indlela eyichaphazela ngayo ibhalansi yakho.|Kenya e le 'ngoe ho bona hore na e ama chelete ea hao e setseng joang.
Mark received|Maka njengokutholiwe|Merk as ontvang|Phawula njengefunyenweyo|Tšoaea e fumanoeng
Mark paid|Maka njengokukhokhiwe|Merk as betaal|Phawula njengehlawulweyo|Tšoaea e lefiloeng
Marked as received|Kumakwe njengokutholiwe|As ontvang gemerk|Iphawulwe njengefunyenweyo|E tšoailoe e fumanoeng
Marked as paid|Kumakwe njengokukhokhiwe|As betaal gemerk|Iphawulwe njengehlawulweyo|E tšoailoe e lefiloeng
Transaction|Ukuthengiselana|Transaksie|Intengiselwano|Tšebelisano
Transaction form|Ifomu lokuthengiselana|Transaksievorm|Ifomu yentengiselwano|Foromo ea tšebelisano
Add transaction|Engeza ukuthengiselana|Voeg transaksie by|Faka intengiselwano|Kenya tšebelisano
Edit transaction|Hlela ukuthengiselana|Wysig transaksie|Hlela intengiselwano|Fetola tšebelisano
Edit transaction {v0}|Hlela ukuthengiselana {v0}|Wysig transaksie {v0}|Hlela intengiselwano {v0}|Fetola tšebelisano {v0}
Record expected and completed payments clearly.|Bhala izinkokhelo ezilindelekile neziqediwe ngokucacile.|Teken verwagte en voltooide betalings duidelik aan.|Bhala ngokucacileyo iintlawulo ezilindelweyo nezigqityiweyo.|Tlaleha litefo tse lebelletsoeng le tse phethiloeng ka ho hlaka.
Description *|Incazelo *|Beskrywing *|Inkcazelo *|Tlhaloso *
Amount (ZAR) *|Inani (ZAR) *|Bedrag (ZAR) *|Isixa (ZAR) *|Chelete (ZAR) *
Date|Usuku|Datum|Umhla|Letsatsi
Status|Isimo|Status|Isimo|Boemo
Category|Isigaba|Kategorie|Udidi|Mokhahlelo
Recurrence (optional)|Ukuphindaphinda (uyazikhethela)|Herhaling (opsioneel)|Ukuphinda (akunyanzelekanga)|Ho pheta (boikhethelo)
Notes (optional)|Amanothi (uyazikhethela)|Notas (opsioneel)|Amanqaku (akunyanzelekanga)|Lintlha (boikhethelo)
Add context|Engeza imininingwane|Voeg besonderhede by|Faka iinkcukacha|Kenya lintlha
Save transaction|Gcina ukuthengiselana|Stoor transaksie|Gcina intengiselwano|Boloka tšebelisano
Save changes|Gcina izinguquko|Stoor veranderinge|Gcina utshintsho|Boloka liphetoho
Transaction saved|Ukuthengiselana kugciniwe|Transaksie gestoor|Intengiselwano igciniwe|Tšebelisano e bolokiloe
Transaction updated|Ukuthengiselana kuvuselelwe|Transaksie opgedateer|Intengiselwano ihlaziyiwe|Tšebelisano e nchafalitsoe
Received / paid|Kutholiwe / kukhokhiwe|Ontvang / betaal|Ifunyenwe / ihlawulwe|E fumanoeng / e lefiloeng
Cancelled|Kukhanseliwe|Gekanselleer|Irhoxisiwe|E hlakotsoeng
Does not repeat|Akuphindi|Herhaal nie|Ayiphindi|Ha e phete
Daily|Nsuku zonke|Daagliks|Yonke imihla|Letsatsi le letsatsi
Weekly|Masonto onke|Weekliks|Rhoqo ngeveki|Beke le beke
Yearly|Minyaka yonke|Jaarliks|Rhoqo ngonyaka|Selemo le selemo
Could not load updated categories. Standard categories are available.|Izigaba ezivuselelwe azilayishekanga. Izigaba ezijwayelekile ziyatholakala.|Kon nie opgedateerde kategorieë laai nie. Standaardkategorieë is beskikbaar.|Iindidi ezihlaziyiweyo azilayishekanga. Iindidi eziqhelekileyo ziyafumaneka.|Mekhahlelo e nchafalitsoeng ha ea laoleha. Mekhahlelo e tloaelehileng e teng.
"""

COPY += r"""
Savings goals|Imigomo yokonga|Spaardoelwitte|Iinjongo zokonga|Lipheo tsa poloko
Savings goal|Umgomo wokonga|Spaardoelwit|Injongo yokonga|Sepheo sa poloko
Goal|Umgomo|Doelwit|Injongo|Sepheo
Goal form|Ifomu lomgomo|Doelwitvorm|Ifomu yenjongo|Foromo ea sepheo
ACTIVE GOAL|UMGOMO OSEBENZAYO|AKTIEWE DOELWIT|INJONGO ESEBENZAYO|SEPHEO SE SEBETSANG
Track contributions manually. FlowShelter does not move money.|Bhala imali oyifakayo ngesandla. I-FlowShelter ayidlulisi imali.|Teken bydraes self aan. FlowShelter skuif nie geld nie.|Bhala iminikelo ngokwakho. I-FlowShelter ayihambisi mali.|Tlaleha chelete eo u e bolokang ka bouena. FlowShelter ha e fetise chelete.
No savings goal yet|Awukabi nomgomo wokonga|Nog geen spaardoelwit nie|Akukho njongo yokonga okwangoku|Ha ho sepheo sa poloko hajoale
Create one to start tracking progress. You record every contribution yourself.|Dala owodwa ukuze uqale ukubona inqubekela phambili. Ubhala yonke imali oyifakayo ngokwakho.|Skep een om jou vordering te begin volg. Jy teken elke bydrae self aan.|Yenza enye ukuze uqale ukulandela inkqubela. Ubhala umnikelo ngamnye ngokwakho.|Theha e le 'ngoe ho qala ho latela tsoelo-pele. U tlaleha chelete e 'ngoe le e 'ngoe ka bouena.
Planning another goal?|Uhlelela omunye umgomo?|Beplan jy nog 'n doelwit?|Uceba enye injongo?|U rera sepheo se seng?
Create a goal for tax, equipment or time off.|Dala umgomo wentela, amathuluzi noma isikhathi sokuphumula.|Skep 'n doelwit vir belasting, toerusting of verlof.|Yenza injongo yerhafu, izixhobo okanye ikhefu.|Theha sepheo sa lekhetho, lisebelisoa kapa nako ea phomolo.
Create another goal|Dala omunye umgomo|Skep nog 'n doelwit|Yenza enye injongo|Theha sepheo se seng
Create goal|Dala umgomo|Skep doelwit|Yenza injongo|Theha sepheo
Edit goal|Hlela umgomo|Wysig doelwit|Hlela injongo|Fetola sepheo
A goal is a target you track yourself. Nothing is transferred automatically.|Umgomo yinto ofuna ukuyifinyelela oyilandelela ngokwakho. Akukho okudluliselwa ngokuzenzakalela.|'n Doelwit is 'n mikpunt wat jy self volg. Niks word outomaties oorgeplaas nie.|Injongo yinto ojolise kuyo oyilandelayo ngokwakho. Akukho nto idluliselwa ngokuzenzekelayo.|Sepheo ke ntho eo u e hahamallang le ho e latela ka bouena. Ha ho letho le fetisoang ka bo lona.
Goal name *|Igama lomgomo *|Doelwitnaam *|Igama lenjongo *|Lebitso la sepheo *
Target amount (ZAR) *|Inani lomgomo (ZAR) *|Teikenbedrag (ZAR) *|Isixa ekujoliswe kuso (ZAR) *|Chelete e reriloeng (ZAR) *
Target amount *|Inani lomgomo *|Teikenbedrag *|Isixa ekujoliswe kuso *|Chelete e reriloeng *
Current saved amount|Imali osuyongile|Huidige gespaarde bedrag|Imali osele uyongile|Chelete e seng e bolokiloe
Target date (optional)|Usuku lomgomo (uyazikhethela)|Teikendatum (opsioneel)|Umhla ekujoliswe kuwo (akunyanzelekanga)|Letsatsi le reriloeng (boikhethelo)
Target date: {v0}|Usuku lomgomo: {v0}|Teikendatum: {v0}|Umhla ekujoliswe kuwo: {v0}|Letsatsi le reriloeng: {v0}
Priority|Ukubaluleka|Prioriteit|Ukubaluleka|Bohlokoa
Priority (optional)|Ukubaluleka (uyazikhethela)|Prioriteit (opsioneel)|Ukubaluleka (akunyanzelekanga)|Bohlokoa (boikhethelo)
Low|Phansi|Laag|Phantsi|Bo tlase
Medium|Phakathi|Medium|Phakathi|Bo mahareng
High|Phezulu|Hoog|Phezulu|Bo phahameng
Saved|Okongiwe|Gespaar|Eyongiweyo|E bolokiloeng
Remaining|Okusele|Oorblywend|Eseleyo|E setseng
Target|Okuhlosiwe|Teiken|Ekujoliswe kuyo|E reriloeng
No date|Alukho usuku|Geen datum nie|Akukho mhla|Ha ho letsatsi
Goal saved|Umgomo ugciniwe|Doelwit gestoor|Injongo igciniwe|Sepheo se bolokiloe
Goal updated|Umgomo uvuselelwe|Doelwit opgedateer|Injongo ihlaziyiwe|Sepheo se nchafalitsoe
Goal reached|Umgomo ufinyelelwe|Doelwit bereik|Injongo ifikelelwe|Sepheo se fihletsoe
75% there|Sekufinyelelwe ku-75%|75% daar|Kufikelelwe kwi-75%|Ho fihletsoe 75%
Halfway there|Sekuphakathi nendawo|Halfpad daar|Sekuphakathi|Ho fihletsoe halofo
First quarter|Ikota yokuqala|Eerste kwart|Ikota yokuqala|Kotara ea pele
Started|Sekuqalile|Begin|Kuqalisiwe|Ho qaliloe
Goal reached · Based on your recorded savings|Umgomo ufinyelelwe · Ngokwemali oyibhalile oyongile|Doelwit bereik · Volgens jou aangetekende spaargeld|Injongo ifikelelwe · Ngokwemali oyibhalileyo oyongileyo|Sepheo se fihletsoe · Ho latela poloko eo u e tlalehileng
Savings progress: {v0} percent|Inqubekela phambili yokonga: amaphesenti angu-{v0}|Spaarvordering: {v0} persent|Inkqubela yokonga: ipesenti eziyi-{v0}|Tsoelo-pele ea poloko: liphesente tse {v0}
{v0} saved of {v1}|Kongiwe {v0} ku-{v1}|{v0} gespaar van {v1}|Kongiwe {v0} kwi-{v1}|Ho bolokiloe {v0} ho {v1}
{v0} of {v1}|{v0} ku-{v1}|{v0} van {v1}|{v0} kwi-{v1}|{v0} ho {v1}
{v0} to your {v1}% milestone|Kusele {v0} ukuze ufinyelele ku-{v1}%|{v0} tot jou {v1}%-mylpaal|Kusele {v0} ukufikelela kwi-{v1}%|Ho setse {v0} ho fihlela mohato oa {v1}%
{v0}% milestone, |Isigaba sika-{v0}%, |{v0}%-mylpaal, |Inqanaba le-{v0}%, |Mohato oa {v0}%, 
reached|kufinyelelwe|bereik|kufikelelwe|o fihletsoe
ahead|kusazofikwa|nog voor|kuseza kufikelelwa|o sa tlang
{v0} is {v1}% funded. Keep going.|Umgomo {v0} usuno-{v1}% wemali. Qhubeka.|{v0} is {v1}% befonds. Hou so aan.|Injongo {v0} ixhaswe nge-{v1}%. Qhubeka.|{v0} e na le {v1}% ea chelete. Tsoela pele.
You reached {v0}!|Uwufinyelele umgomo {v0}!|Jy het {v0} bereik!|Uyifikelele injongo {v0}!|U fihletse {v0}!
Open savings goal {v0}|Vula umgomo wokonga {v0}|Maak spaardoelwit {v0} oop|Vula injongo yokonga {v0}|Bula sepheo sa poloko {v0}
Set up your plan|Yakha uhlelo lwakho|Stel jou plan op|Yakha isicwangciso sakho|Theha moralo oa hao
Step {v0} of {v1}|Isinyathelo {v0} kwezingu-{v1}|Stap {v0} van {v1}|Inyathelo {v0} kwangama-{v1}|Mohato oa {v0} ho e {v1}
Continue|Qhubeka|Gaan voort|Qhubeka|Tsoela pele
Save & exit|Gcina bese uphuma|Stoor en verlaat|Gcina uze uphume|Boloka 'me u tsoe
Tell us about your work|Sitshele ngomsebenzi wakho|Vertel ons van jou werk|Sixelele ngomsebenzi wakho|Re bolelle ka mosebetsi oa hao
This helps us shape a useful first cash-flow plan. No client details needed.|Lokhu kusisiza sakhe uhlelo lokuqala lokuhamba kwemali oluwusizo. Akudingeki imininingwane yamakhasimende.|Dit help ons om 'n nuttige eerste kontantvloeiplan op te stel. Geen kliëntbesonderhede is nodig nie.|Oku kusinceda sakhe isicwangciso sokuqala esiluncedo sokuhamba kwemali. Akufuneki nkcukacha zabathengi.|Sena se re thusa ho theha moralo oa pele o molemo oa phallo ea chelete. Ha ho hlokahale lintlha tsa bareki.
Type of freelance work *|Uhlobo lomsebenzi ozisebenzayo *|Soort vryskutwerk *|Uhlobo lomsebenzi ozisebenzelayo *|Mofuta oa mosebetsi oa boikemelo *
Income pattern|Indlela imali engena ngayo|Inkomstepatroon|Indlela ingeniso efika ngayo|Mokhoa oa chelete e kenang
Fixed|Okungaguquki|Vas|Esisigxina|E tsitsitseng
Irregular|Okungajwayelekile|Wisselend|Engafiki rhoqo|E sa tsitsang
Mixed|Okuxubile|Gemeng|Exubeneyo|E tsoakiloeng
Typical income amount (optional)|Imali ejwayelekile engenayo (uyazikhethela)|Gewone inkomstebedrag (opsioneel)|Isixa sengeniso esiqhelekileyo (akunyanzelekanga)|Chelete e kenang ka tloaelo (boikhethelo)
Next expected payment date (optional)|Usuku lwenkokhelo elandelayo oyilindele (uyazikhethela)|Datum van volgende verwagte betaling (opsioneel)|Umhla wentlawulo elandelayo elindelweyo (akunyanzelekanga)|Letsatsi la tefo e latelang e lebelletsoeng (boikhethelo)
Next expected payment amount (optional)|Inani lenkokhelo elandelayo oyilindele (uyazikhethela)|Bedrag van volgende verwagte betaling (opsioneel)|Isixa sentlawulo elandelayo elindelweyo (akunyanzelekanga)|Chelete ea tefo e latelang e lebelletsoeng (boikhethelo)
Currency|Uhlobo lwemali|Geldeenheid|Uhlobo lwemali|Mofuta oa chelete
ZAR — South African rand|ZAR — Irandi laseNingizimu Afrika|ZAR — Suid-Afrikaanse rand|ZAR — IRandi yaseMzantsi Afrika|ZAR — Ranta ea Afrika Boroa
USD — US dollar|USD — Idola laseMelika|USD — Amerikaanse dollar|USD — IDola yaseMelika|USD — Dolara ea Amerika
EUR — Euro|EUR — I-Euro|EUR — Euro|EUR — IYuro|EUR — Yuro
GBP — British pound|GBP — Iphawundi laseBrithani|GBP — Britse pond|GBP — IPonti yaseBritani|GBP — Ponto ea Brithani
What do you have available now?|Unamalini ongayisebenzisa manje?|Wat het jy nou beskikbaar?|Unantoni ekhoyo ngoku?|U na le chelete e kae hona joale?
Only include money you can currently use. Do not include expected payments.|Faka kuphela imali ongayisebenzisa manje. Ungafaki izinkokhelo ozilindele.|Sluit slegs geld in wat jy tans kan gebruik. Moenie verwagte betalings insluit nie.|Faka kuphela imali onokuyisebenzisa ngoku. Ungafaki iintlawulo ozilindeleyo.|Kenya feela chelete eo u ka e sebelisang hona joale. U se ke ua kenya litefo tse lebelletsoeng.
Current available balance *|Ibhalansi etholakala manje *|Huidige beskikbare saldo *|Ibhalansi ekhoyo ngoku *|Chelete e setseng e fumanehang hona joale *
Existing savings (optional)|Imali osuyongile (uyazikhethela)|Bestaande spaargeld (opsioneel)|Imali esele yongiwe (akunyanzelekanga)|Poloko e seng e le teng (boikhethelo)
Use money you have right now. Payments you are waiting on belong on the next step, so they are not counted twice.|Sebenzisa imali onayo manje. Izinkokhelo ozilindele zingena esinyathelweni esilandelayo ukuze zingabalwa kabili.|Gebruik geld wat jy nou het. Betalings waarop jy wag hoort by die volgende stap, sodat dit nie twee keer getel word nie.|Sebenzisa imali onayo ngoku. Iintlawulo ozilindeleyo zingena kwinyathelo elilandelayo ukuze zingabalwa kabini.|Sebelisa chelete eo u nang le eona hona joale. Litefo tseo u li emetseng li kena mohatong o latelang hore li se ke tsa baloa habeli.
What income are you expecting?|Iyiphi imali engenayo oyilindele?|Watter inkomste verwag jy?|Yeyiphi ingeniso oyilindeleyo?|U lebelletse chelete efe e kenang?
Expected money is kept separate until you mark it received.|Imali oyilindele igcinwa yodwa uze uyimake njengokutholiwe.|Verwagte geld bly apart totdat jy dit as ontvang merk.|Imali elindelweyo igcinwa yodwa ude uyiphawule njengefunyenweyo.|Chelete e lebelletsoeng e aroloa ho fihlela u e tšoaea e fumanoeng.
New income|Imali entsha engenayo|Nuwe inkomste|Ingeniso entsha|Chelete e ncha e kenang
Income source|Umthombo wemali engenayo|Inkomstebron|Umthombo wengeniso|Mohloli oa chelete e kenang
Amount|Inani|Bedrag|Isixa|Chelete
Expected date|Usuku olulindelekile|Verwagte datum|Umhla olindelweyo|Letsatsi le lebelletsoeng
Remove|Susa|Verwyder|Susa|Tlosa
Leave an item out if you are not sure yet.|Yeka into uma ungakaqiniseki ngayo.|Laat 'n item uit as jy nog nie seker is nie.|Yishiye into ukuba awukaqiniseki ngayo.|Tlohela ntho haeba u e-so tiisehe ka eona.
What must you pay?|Yini okufanele uyikhokhe?|Wat moet jy betaal?|Yintoni ekufuneka uyihlawule?|U tlameha ho lefa eng?
Add essential expenses and upcoming commitments.|Engeza izindleko ezibalulekile nezibopho ezizayo.|Voeg noodsaaklike uitgawes en komende verpligtinge by.|Faka iindleko ezibalulekileyo nezibophelelo ezizayo.|Kenya litšenyehelo tsa bohlokoa le boitlamo bo tlang.
Due date|Usuku lokukhokha|Betaaldatum|Umhla wokuhlawula|Letsatsi la tefo
Only add bills you have to pay. Leave an item out if you are not sure yet.|Engeza kuphela izikweletu okufanele uzikhokhe. Yeka into uma ungakaqiniseki ngayo.|Voeg slegs rekeninge by wat jy moet betaal. Laat 'n item uit as jy nog nie seker is nie.|Faka kuphela amatyala ekufuneka uwahlawule. Yishiye into ukuba awukaqiniseki ngayo.|Kenya feela likoloto tseo u tlamehang ho li lefa. Tlohela ntho haeba u e-so tiisehe ka eona.
Set your first savings goal|Beka umgomo wakho wokuqala wokonga|Stel jou eerste spaardoelwit|Beka injongo yakho yokuqala yokonga|Beha sepheo sa hao sa pele sa poloko
Skip for now|Yeqa okwamanje|Slaan vir eers oor|Tsiba okwangoku|Tlola hajoale
Already saved|Osuyongile|Reeds gespaar|Osele uyongile|E seng e bolokiloe
Your starting picture|Isithombe sakho sokuqala|Jou beginprentjie|Umfanekiso wakho wokuqala|Pono ea hao ea pele
This is an estimate built from what you told us.|Lesi yisilinganiso esisekelwe kulokho ositshele khona.|Dit is 'n raming op grond van wat jy ons vertel het.|Olu luqikelelo olusekelwe koko usixelele kona.|Ena ke khakanyo e thehiloeng ho seo u re boleletseng sona.
No expected payment yet|Awukabi nankokhelo oyilindele|Nog geen verwagte betaling nie|Akukho ntlawulo ilindelweyo okwangoku|Ha ho tefo e lebelletsoeng hajoale
Next income  +{v0}  {v1}|Imali elandelayo engenayo  +{v0}  {v1}|Volgende inkomste  +{v0}  {v1}|Ingeniso elandelayo  +{v0}  {v1}|Chelete e latelang e kenang  +{v0}  {v1}
Projected after known events|Okulindelwe ngemva kwezehlakalo ezaziwayo|Verwag ná bekende gebeure|Eqikelelweyo emva kweziganeko ezaziwayo|E hakantsoeng ka mor'a liketsahalo tse tsejoang
Before your next|Ngaphambi kokulandelayo|Voor jou volgende|Phambi kokulandelayo|Pele ho e latelang
Essential commitments|Izibopho ezibalulekile|Noodsaaklike verpligtinge|Izibophelelo ezibalulekileyo|Boitlamo ba bohlokoa
Your forecast is an estimate. It updates as you add payments and expenses, so nothing here is locked in.|Isibikezelo sakho siyisilinganiso. Siyashintsha uma ufaka izinkokhelo nezindleko, ngakho akukho okubekiwe unomphela.|Jou vooruitskatting is 'n raming. Dit verander soos jy betalings en uitgawes byvoeg; niks hier is vas nie.|Uqikelelo lwakho luyatshintsha xa ufaka iintlawulo neendleko; akukho nto imiselwe ngokusisigxina.|Khakanyo ea hao e fetoha ha u kenya litefo le litšenyehelo; ha ho letho le behiloeng ka ho sa feleng.
Go to my dashboard|Iya ekhasini lami eliyinhloko|Gaan na my kontroleskerm|Yiya kwiphepha lam eliphambili|E-ea leqepheng la ka la sehlooho
e.g. Graphic designer|isb. Umklami wezithombe|bv. Grafiese ontwerper|umz. Umyili wemizobo|mohl. Moqapi oa litšoantšo
e.g. Mokoena Studio project|isb. Iphrojekthi ye-Mokoena Studio|bv. Mokoena Studio-projek|umz. Iprojekthi ye-Mokoena Studio|mohl. Morero oa Mokoena Studio
e.g. Apartment rent|isb. Irenti yefulethi|bv. Woonstelhuur|umz. Irenti yeflethi|mohl. Rente ea folete
e.g. Emergency buffer|isb. Imali yezimo eziphuthumayo|bv. Noodfonds|umz. Ingxowa yexesha likaxakeka|mohl. Poloko ea tšohanyetso
e.g. Tax reserve|isb. Imali ebekelwe intela|bv. Belastingreserwe|umz. Imali ebekelwe irhafu|mohl. Chelete e behelletsoeng lekhetho
e.g. Project payment|isb. Inkokhelo yephrojekthi|bv. Projekbetaling|umz. Intlawulo yeprojekthi|mohl. Tefo ea morero
Discard your changes?|Ulahle izinguquko zakho?|Gooi jou veranderinge weg?|Lahla utshintsho lwakho?|Lahla liphetoho tsa hao?
Your changes have not been saved.|Izinguquko zakho azikagcinwa.|Jou veranderinge is nie gestoor nie.|Utshintsho lwakho alukagcinwa.|Liphetoho tsa hao ha lia bolokoa.
Keep editing|Qhubeka uhlela|Hou aan wysig|Qhubeka uhlela|Tsoela pele ho fetola
Discard changes|Lahla izinguquko|Gooi veranderinge weg|Lahla utshintsho|Lahla liphetoho
Try again|Zama futhi|Probeer weer|Zama kwakhona|Leka hape
Review|Buyekeza|Hersien|Hlola|Hlahloba
Something needs your attention.|Kukhona okudinga ukunakwa nguwe.|Iets het jou aandag nodig.|Kukho into efuna ingqalelo yakho.|Ho na le ntho e hlokang tlhokomelo ea hao.
{v0}, selected|{v0}, kukhethiwe|{v0}, gekies|{v0}, kukhethiwe|{v0}, e khethiloe
Not set|Akukasethwa|Nie ingestel nie|Akukamiselwa|Ha e so behoe
expected|okulindelekile|verwag|okulindelweyo|e lebelletsoeng
invalid|akulungile|ongeldig|ayichanekanga|ha e nepahale
Work type is required.|Uhlobo lomsebenzi luyadingeka.|Soort werk is verpligtend.|Uhlobo lomsebenzi luyafuneka.|Mofuta oa mosebetsi oa hlokahala.
Available balance is required.|Ibhalansi etholakalayo iyadingeka.|Beskikbare saldo is verpligtend.|Ibhalansi ekhoyo iyafuneka.|Chelete e setseng e fumanehang ea hlokahala.
Give each income a source.|Nikeza umthombo wemali ngayinye engenayo.|Gee elke inkomste 'n bron.|Nika ingeniso nganye umthombo.|Fana ka mohloli oa chelete ka 'ngoe e kenang.
Give each expense a name.|Nikeza izindleko ngazinye igama.|Gee elke uitgawe 'n naam.|Nika inkcitho nganye igama.|Fana ka lebitso la tšenyehelo ka 'ngoe.
Enter an amount for {v0}.|Faka inani le-{v0}.|Voer 'n bedrag vir {v0} in.|Faka isixa se-{v0}.|Kenya chelete ea {v0}.
Goal name is required.|Igama lomgomo liyadingeka.|Doelwitnaam is verpligtend.|Igama lenjongo liyafuneka.|Lebitso la sepheo lea hlokahala.
Target amount is required.|Inani lomgomo liyadingeka.|Teikenbedrag is verpligtend.|Isixa ekujoliswe kuso siyafuneka.|Chelete e reriloeng ea hlokahala.
Target must be greater than zero.|Umgomo kufanele ube mkhulu kunoziro.|Die teiken moet groter as nul wees.|Isixa ekujoliswe kuso kufuneka sibe ngaphezu kweqanda.|Chelete e reriloeng e tlameha ho feta noto.
Saved amount cannot be negative.|Imali eyongiwe ayikwazi ukuba ngaphansi kukaziro.|Die gespaarde bedrag kan nie negatief wees nie.|Imali eyongiweyo ayinakuba ngaphantsi kweqanda.|Chelete e bolokiloeng e ke ke ea ba ka tlase ho noto.
Enter a goal name.|Faka igama lomgomo.|Voer 'n doelwitnaam in.|Faka igama lenjongo.|Kenya lebitso la sepheo.
Enter a target amount.|Faka inani lomgomo.|Voer 'n teikenbedrag in.|Faka isixa ekujoliswe kuso.|Kenya chelete e reriloeng.
Description is required.|Incazelo iyadingeka.|Beskrywing is verpligtend.|Inkcazelo iyafuneka.|Tlhaloso ea hlokahala.
Enter a description.|Faka incazelo.|Voer 'n beskrywing in.|Faka inkcazelo.|Kenya tlhaloso.
Amount is required.|Inani liyadingeka.|Bedrag is verpligtend.|Isixa siyafuneka.|Chelete ea hlokahala.
Enter an amount.|Faka inani.|Voer 'n bedrag in.|Faka isixa.|Kenya chelete.
Amount must be greater than zero.|Inani kufanele libe likhulu kunoziro.|Die bedrag moet groter as nul wees.|Isixa kufuneka sibe ngaphezu kweqanda.|Chelete e tlameha ho feta noto.
Date is required.|Usuku luyadingeka.|Datum is verpligtend.|Umhla uyafuneka.|Letsatsi lea hlokahala.
Choose a date.|Khetha usuku.|Kies 'n datum.|Khetha umhla.|Khetha letsatsi.
Enter a finite amount.|Faka inani lemali elivumelekile.|Voer 'n eindige bedrag in.|Faka isixa semali esisebenzayo.|Kenya chelete e nepahetseng.
“{v0}” is not a valid amount.|“{v0}” akulona inani elivumelekile.|“{v0}” is nie 'n geldige bedrag nie.|“{v0}” ayisosixa esisebenzayo.|“{v0}” ha se chelete e nepahetseng.
Can't load your plan|Uhlelo lwakho alulayishekanga|Kan nie jou plan laai nie|Isicwangciso sakho asilayishekanga|Moralo oa hao ha o laolehe
Can't reach the Flow Shelter server. Check your connection.|Asikwazi ukufinyelela kuseva ye-Flow Shelter. Hlola uxhumano lwakho.|Kan nie die Flow Shelter-bediener bereik nie. Gaan jou verbinding na.|Asikwazi ukufikelela kwiseva ye-Flow Shelter. Jonga uqhagamshelo lwakho.|Ha re khone ho hokela ho seva ea Flow Shelter. Hlahloba khokahano ea hao.
The server took too long to respond. Try again.|Iseva ithathe isikhathi eside ukuphendula. Zama futhi.|Die bediener het te lank geneem om te reageer. Probeer weer.|Iseva ithathe ixesha elide ukuphendula. Zama kwakhona.|Seva e nkile nako e telele ho araba. Leka hape.
Something went wrong ({v0}).|Kukhona okungahambanga kahle ({v0}).|Iets het verkeerd geloop ({v0}).|Kukho into engahambanga kakuhle ({v0}).|Ho bile le phoso ({v0}).
Something went wrong. Please try again.|Kukhona okungahambanga kahle. Sicela uzame futhi.|Iets het verkeerd geloop. Probeer asseblief weer.|Kukho into engahambanga kakuhle. Nceda uzame kwakhona.|Ho bile le phoso. Ka kopo leka hape.
Could not refresh. Showing the last loaded figures. {v0}|Asikwazanga ukuvuselela. Kuboniswa izinombolo ezilayishwe ekugcineni. {v0}|Kon nie verfris nie. Die laaste gelaaide syfers word gewys. {v0}|Asikwazanga ukuhlaziya. Kuboniswa amanani okugqibela alayishiweyo. {v0}|Ha rea khona ho nchafatsa. Ho bontšoa lipalo tse laotsoeng qetellong. {v0}
Could not update this period. Showing the last loaded plan. |Asikwazanga ukuvuselela lesi sikhathi. Kuboniswa uhlelo olulayishwe ekugcineni. |Kon nie hierdie tydperk opdateer nie. Die laaste gelaaide plan word gewys. |Asikwazanga ukuhlaziya eli xesha. Kuboniswa isicwangciso sokugqibela esilayishiweyo. |Ha rea khona ho nchafatsa nako ena. Ho bontšoa moralo o laotsoeng qetellong. 
Showing the last loaded transactions. |Kuboniswa ukuthengiselana okulayishwe ekugcineni. |Die laaste gelaaide transaksies word gewys. |Kuboniswa iintengiselwano zokugqibela ezilayishiweyo. |Ho bontšoa litšebelisano tse laotsoeng qetellong. 
The planned balance chart could not be refreshed.|Ishadi lebhalansi ehleliwe alivuselelwanga.|Die beplande saldografiek kon nie verfris word nie.|Itshathi yebhalansi ecwangcisiweyo ayikwazanga ukuhlaziywa.|Chate ea chelete e setseng e reriloeng ha ea nchafala.
Could not save your language preference. Try again.|Asikwazanga ukugcina ulimi olukhethile. Zama futhi.|Kon nie jou taalvoorkeur stoor nie. Probeer weer.|Asikwazanga ukugcina ulwimi olukhethileyo. Zama kwakhona.|Ha rea khona ho boloka puo eo u e khethileng. Leka hape.
Optional. You can create or change goals at any time.|Uyazikhethela. Ungadala noma ushintshe imigomo noma nini.|Opsioneel. Jy kan enige tyd doelwitte skep of verander.|Akunyanzelekanga. Ungenza okanye utshintshe iinjongo nangaliphi na ixesha.|Ke boikhethelo. U ka theha kapa oa fetola lipheo neng kapa neng.
+ Add another income|+ Engeza omunye umthombo wemali|+ Voeg nog inkomste by|+ Faka enye ingeniso|+ Kenya chelete e 'ngoe e kenang
+ Add another expense|+ Engeza ezinye izindleko|+ Voeg nog 'n uitgawe by|+ Faka enye inkcitho|+ Kenya tšenyehelo e 'ngoe
Review & continue|Buyekeza bese uqhubeka|Hersien en gaan voort|Hlola uze uqhubeke|Hlahloba 'me u tsoele pele
Keep going.|Qhubeka.|Hou so aan.|Qhubeka.|Tsoela pele.
Housing|Izindlu|Behuising|Izindlu|Bolulo
Utilities|Izinsiza|Munisipale dienste|Iinkonzo|Litšebeletso
Food|Ukudla|Kos|Ukutya|Lijo
Transport|Ezokuthutha|Vervoer|Ezothutho|Lipalangoang
Subscriptions|Okubhaliselwe|Intekeninge|Imirhumo|Litefiso tsa ngoliso
Equipment|Amathuluzi|Toerusting|Izixhobo|Lisebelisoa
Tax|Intela|Belasting|Irhafu|Lekhetho
Other|Okunye|Ander|Ezinye|Tse ling
Client payment|Inkokhelo yekhasimende|Kliëntbetaling|Intlawulo yomthengi|Tefo ea moreki
Salary|Umholo|Salaris|Umvuzo|Moputso
Refund|Imali ebuyisiwe|Terugbetaling|Imbuyekezo|Puseletso
January|uMasingana|Januarie|EyoMqungu|Pherekhong
February|uNhlolanja|Februarie|EyoMdumba|Hlakola
March|uNdasa|Maart|EyoKwindla|Hlakubele
April|uMbasa|April|UTshazimpuzi|Mmesa
May|uNhlaba|Mei|UCanzibe|Mots'eanong
June|uNhlangulana|Junie|EyeSilimela|Phuptjane
July|uNtulikazi|Julie|EyeKhala|Phupu
August|uNcwaba|Augustus|EyeThupha|Phato
September|uMandulo|September|EyoMsintsi|Loetse
October|uMfumfu|Oktober|EyeDwarha|Mphalane
November|uLwezi|November|EyeNkanga|Pulungoana
December|uZibandlela|Desember|EyoMnga|Tšitoe
today|namuhla|vandag|namhlanje|kajeno
Tomorrow|Kusasa|Môre|Ngomso|Hosane
On track|Usendleleni|Op koers|Usendleleni|E tseleng
Completed|Kuqediwe|Voltooi|Kugqityiwe|E phethiloeng
Overdue|Kudlule isikhathi|Agterstallig|Idlulelwe lixesha|E fetetsoeng ke nako
Depends on payment arriving|Kuncike ekufikeni kwenkokhelo|Hang af van betaling wat inkom|Kuxhomekeke ekufikeni kwentlawulo|Ho latela ho fihla ha tefo
Authentication failed. Check your email and password.|Ukungena akuphumelelanga. Hlola i-imeyili nephasiwedi yakho.|Aanmelding het misluk. Gaan jou e-pos en wagwoord na.|Ukungena akuphumelelanga. Jonga i-imeyile negama lokugqitha.|Ho kena ho hlotsoe. Hlahloba imeile le phasewete ea hao.
Please check the entered details.|Sicela uhlole imininingwane oyifakile.|Gaan asseblief die ingevoerde besonderhede na.|Nceda ujonge iinkcukacha ozifakileyo.|Ka kopo hlahloba lintlha tseo u li kentseng.
Email already registered|I-imeyili isibhalisiwe|E-pos reeds geregistreer|I-imeyile sele ibhalisiwe|Imeile e se e ngolisitsoe
Incorrect email or password|I-imeyili noma iphasiwedi ayilungile|Verkeerde e-pos of wagwoord|I-imeyile okanye igama lokugqitha alichanekanga|Imeile kapa phasewete e fosahetse
"""

COPY += r"""
Today|Namuhla|Vandag|Namhlanje|Kajeno
Ending balance|Ibhalansi yokugcina|Eindsaldo|Ibhalansi yokugqibela|Chelete e setseng qetellong
Confirmed|Kuqinisekisiwe|Bevestig|Iqinisekisiwe|E netefalitsoeng
Not yet confirmed|Akukaqinisekiswa|Nog nie bevestig nie|Ayikaqinisekiswa|Ha e so netefatsoe
Repeats|Kuyaphinda|Herhaal|Iyaphinda|E ea pheta
Planned savings allocation|Imali ehlelelwe ukongiwa|Beplande spaartoewysing|Imali ebekelwe ukonga|Chelete e reretsoeng poloko
A plan, not a transfer|Uhlelo, akukona ukudluliswa kwemali|'n Plan, nie 'n oorplasing nie|Sisicwangciso, asilodluliselo lwemali|Ke moralo, ha se phetiso
Reached|Kufinyelelwe|Bereik|Kufikelelwe|E fihletsoe
No date set|Usuku alukabekwa|Geen datum ingestel nie|Akukho mhla ubekiweyo|Ha ho letsatsi le behiloeng
Past due|Kudlule usuku|Verstreke betaaldatum|Idlulelwe ngumhla|Letsatsi le fetile
Behind|Usalele emuva|Agter|Usemva|E salletseng morao
Finish onboarding to get accurate forecasts.|Qedela ukusetha ukuze uthole izibikezelo ezinembile.|Voltooi die opstelling vir akkurate vooruitskattings.|Gqibezela ukuseta ukuze ufumane uqikelelo oluchanekileyo.|Qeta ho theha moralo ho fumana likhakanyo tse nepahetseng.
Your commitments ({v0}) are more than what you have available ({v1}).|Izibopho zakho ({v0}) zingaphezu kwemali onayo ({v1}).|Jou verpligtinge ({v0}) is meer as wat jy beskikbaar het ({v1}).|Izibophelelo zakho ({v0}) zingaphezu kwemali onayo ({v1}).|Boitlamo ba hao ({v0}) bo feta chelete eo u nang le eona ({v1}).
{v0} payment was due on {v1} but has not arrived.|Inkokhelo ye-{v0} bekumele ifike ngo-{v1} kodwa ayikafiki.|Die betaling van {v0} was op {v1} verskuldig, maar het nog nie ingekom nie.|Intlawulo ye-{v0} bekufanele ifike ngo-{v1} kodwa ayikafiki.|Tefo ea {v0} e ne e lokela ho fihla ka {v1} empa ha e so fihle.
{v0} payment is still expected on {v1}.|Inkokhelo ye-{v0} isalindelekile ngo-{v1}.|Die betaling van {v0} word steeds op {v1} verwag.|Intlawulo ye-{v0} isalindelwe ngo-{v1}.|Tefo ea {v0} e sa lebelletsoe ka {v1}.
You reached your '{v0}' goal.|Uwufinyelele umgomo wakho othi '{v0}'.|Jy het jou '{v0}'-doelwit bereik.|Uyifikelele injongo yakho ethi '{v0}'.|U fihletse sepheo sa hao sa '{v0}'.
'{v0}' is due in {v1} day(s) and nothing has been saved yet.|Kusele izinsuku ezingu-{v1} kumgomo othi '{v0}' futhi akukongiwa lutho okwamanje.|'{v0}' is oor {v1} dag(e) verskuldig en niks is nog gespaar nie.|Kusele iintsuku eziyi-{v1} kwinjongo ethi '{v0}' kwaye akukho nto yongiweyo okwangoku.|Ho setse matsatsi a {v1} bakeng sa '{v0}' 'me ha ho letho le bolokiloeng hajoale.
Add what you have available so projections are accurate.|Faka imali onayo ukuze izibikezelo zinembile.|Voer in wat jy beskikbaar het sodat vooruitskattings akkuraat is.|Faka imali onayo ukuze uqikelelo luchaneke.|Kenya chelete eo u nang le eona hore likhakanyo li nepahale.
Onboarding is incomplete|Ukusetha akukapheli|Opstelling is onvolledig|Ukuseta akukagqitywa|Ho theha moralo ha ho so phetheloe
Jan|Jan|Jan|Mqu|Phe
Feb|Feb|Feb|Mdu|Hla
Mar|Mas|Mrt|Kwi|Hlb
Apr|Mba|Apr|Tsh|Mme
Jun|Nhl|Jun|Sil|Phu
Jul|Ntu|Jul|Kha|Php
Aug|Ncw|Aug|Thu|Pha
Sep|Man|Sep|Msi|Loe
Oct|Mfu|Okt|Dwa|Mph
Nov|Lwe|Nov|Nka|Pul
Dec|Zib|Des|Mga|Tši
"""

COPY += r"""
Saving|Siyagcina|Besig om te stoor|Siyagcina|Ho bolokoa
expected payment|inkokhelo elindelekile|verwagte betaling|intlawulo elindelweyo|tefo e lebelletsoeng
your goal|umgomo wakho|jou doelwit|injongo yakho|sepheo sa hao
"""

CATALOGS = {code: {} for code in ("zu", "af", "xh", "st")}
for row in COPY.strip().splitlines():
    if not row.strip():
        continue
    source, *translations = row.split("|")
    if len(translations) != 4:
        raise ValueError(f"Invalid translation row: {source}")
    for language, translated in zip(CATALOGS, translations):
        CATALOGS[language][source.replace("\\n", "\n")] = translated.replace("\\n", "\n")

