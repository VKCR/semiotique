# This example database is AI-generated and may contain inaccurate claims or
# interpretations. Treat it as demo content, not as an authoritative source.
# These are illustrative reading notes, not quotations from published works.
# Embeddings are empty here; load_into_db() computes and stores them in the DB.

import struct
from datetime import UTC, datetime

from notetaker import notedb
from notetaker.models import Note
from notetaker.utils import compute_embedding


def load_into_db() -> None:
    """Reset the database, then insert examples with their original IDs and timestamps."""
    notedb.drop_db()
    notedb.init_db()

    # Generate embeddings before opening the write transaction.
    embeddings = [
        struct.pack(
            f"{notedb.EMBEDDING_DIMENSIONS}f", *compute_embedding(note.content)
        )
        for note in notes
    ]
    links = {
        tuple(sorted((note.id, linked_id)))
        for note in notes
        for linked_id in note.linked_ids
    }

    with notedb._connect() as connection, connection:
        connection.executemany(
            "INSERT INTO notes (id, created_at, content) VALUES (?, ?, ?)",
            ((note.id, note.created_at.isoformat(), note.content) for note in notes),
        )
        connection.executemany(
            "INSERT INTO note_embeddings (note_id, embedding) VALUES (?, ?)",
            ((note.id, embedding) for note, embedding in zip(notes, embeddings)),
        )
        connection.executemany(
            "INSERT INTO categories (note_id, category) VALUES (?, ?)",
            ((note.id, category) for note in notes for category in note.categories),
        )
        connection.executemany(
            "INSERT INTO links (note_id_1, note_id_2) VALUES (?, ?)",
            sorted(links),
        )


def _note(number: int, category: str, content: str) -> Note:
    """Build a demo note linked to the other four notes in its thematic cluster."""
    cluster_start = ((number - 1) // 5) * 5 + 1
    return Note(
        id=f"reading-{number:03d}",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        categories=[category],
        linked_ids=[
            f"reading-{other:03d}"
            for other in range(cluster_start, cluster_start + 5)
            if other != number
        ],
        content=content,
        embedding=[],
    )


notes: list[Note] = [
    # Cluster 1: Conformity and dissent.
    _note(
        1, "politics",
        "Party discipline and dissent. A political party can coordinate collective "
        "action by expecting members to support an agreed position. The same "
        "expectation can make disagreement costly and hide doubts within the group.",
    ),
    _note(
        2, "psychology",
        "Conformity under social pressure. People sometimes adopt a group's answer "
        "despite private reservations. Agreement may reflect a desire to belong "
        "rather than a genuine change of belief.",
    ),
    _note(
        3, "sociology",
        "Informal sanctions. Ridicule, exclusion, and loss of standing can enforce "
        "a norm without written rules. Reading question: how much apparent "
        "consensus is sustained by the anticipated cost of speaking differently?",
    ),
    _note(
        4, "literature",
        "Conformity in The Emperor's New Clothes. The tale makes public agreement "
        "look fragile: each person has reasons to repeat what others appear to "
        "believe. A dissenting voice interrupts that performance of certainty.",
    ),
    _note(
        5, "science",
        "Replication and scientific disagreement. Independent attempts to reproduce "
        "a result can challenge an accepted claim. Agreement becomes more "
        "informative when researchers have opportunities to discover errors.",
    ),
    # Cluster 2: Trust and cooperation.
    _note(
        6, "economics",
        "Repeated interaction and cooperation. A trading partner's future behavior "
        "can matter more than a short-term gain from cheating. Reputation may "
        "support exchange when a contract cannot specify every contingency.",
    ),
    _note(
        7, "philosophy",
        "Promises and obligation. A promise invites another person to rely on a "
        "future action. Its moral significance involves that reliance as well as "
        "the speaker's intention at the time of making it.",
    ),
    _note(
        8, "history",
        "Merchant networks and trust. Some long-distance trading communities used "
        "reputation and recurring relationships to manage uncertainty. Such "
        "networks could facilitate exchange while excluding outsiders.",
    ),
    _note(
        9, "anthropology",
        "Gift exchange and continuing relationships. In some settings, giving "
        "creates expectations of acknowledgment or return. A gift can establish "
        "an ongoing relationship rather than conclude a transaction.",
    ),
    _note(
        10, "education",
        "Trust in peer feedback. Students may share unfinished work more openly "
        "when criticism is specific and respectful. Repeated constructive exchanges "
        "can make vulnerability a manageable part of learning.",
    ),
    # Cluster 3: Authority and legitimacy.
    _note(
        11, "politics",
        "Legitimacy beyond force. A government may secure compliance because "
        "people regard its procedures or institutions as rightful. This differs "
        "from obedience motivated primarily by fear of punishment.",
    ),
    _note(
        12, "psychology",
        "Authority cues and judgment. Titles, uniforms, and institutional settings "
        "can shape how credible an instruction seems. Reading question: when "
        "does recognition of expertise become uncritical deference?",
    ),
    _note(
        13, "sociology",
        "Routinized authority. Offices and procedures can make authority survive "
        "the departure of a particular leader. People obey a role whose "
        "expectations are socially established, not only an individual.",
    ),
    _note(
        14, "literature",
        "Authority in Kafka's The Trial. Josef K. encounters a judicial apparatus "
        "whose procedures remain obscure. The novel invites reflection on how "
        "institutional power operates when its justification is inaccessible.",
    ),
    _note(
        15, "science",
        "Expertise and inspectable evidence. Scientific authority is more useful "
        "when methods and uncertainty can be examined. A researcher's reputation "
        "can guide attention but cannot establish a claim by itself.",
    ),
    # Cluster 4: Scarcity and allocation.
    _note(
        16, "economics",
        "Opportunity cost. Choosing one use of a scarce resource forgoes another. "
        "A free service can still have a cost in time, attention, or displaced "
        "alternatives even when no money changes hands.",
    ),
    _note(
        17, "philosophy",
        "Justice under scarcity. Equal shares, priority to need, and maximizing "
        "total benefit can recommend different allocations. A disagreement about "
        "distribution may therefore express competing values rather than bad arithmetic.",
    ),
    _note(
        18, "history",
        "Wartime rationing. Ration systems have attempted to distribute limited "
        "supplies through administrative rules. Their operation reveals tensions "
        "between equal treatment, differing needs, and unofficial markets.",
    ),
    _note(
        19, "anthropology",
        "Sharing food and social obligations. Rules about who receives food can "
        "express kinship, status, or hospitality. Scarcity is experienced through "
        "local expectations about who owes what to whom.",
    ),
    _note(
        20, "education",
        "Allocating classroom attention. A teacher's time is limited, while "
        "students' needs differ. Giving every student identical attention and "
        "helping each student reach a threshold are different allocation goals.",
    ),
    # Cluster 5: Collective memory.
    _note(
        21, "politics",
        "Commemoration and political identity. Official anniversaries select "
        "events that a community is invited to remember together. Disputes about "
        "monuments can also be disputes about membership and public recognition.",
    ),
    _note(
        22, "psychology",
        "Memory as reconstruction. Remembering is not simply replaying a stored "
        "record. Present concerns and later information can shape how an "
        "experience is recalled and narrated.",
    ),
    _note(
        23, "sociology",
        "Social frameworks of memory. Families, institutions, and communities "
        "supply occasions and language for remembering. A shared past is "
        "maintained through repeated practices as well as individual recollection.",
    ),
    _note(
        24, "literature",
        "Involuntary memory in Proust. A sensory experience can become an opening "
        "into a remembered world. The literary treatment suggests a contrast "
        "between deliberate chronology and the felt return of an experience.",
    ),
    _note(
        25, "science",
        "Archives as scientific memory. Preserved observations allow later "
        "researchers to revisit old conclusions. What an archive contains depends "
        "on past instruments, recording choices, and preservation practices.",
    ),
    # Cluster 6: Institutions and path dependence.
    _note(
        26, "economics",
        "Switching costs and path dependence. An established arrangement may "
        "persist because changing it requires coordination, training, or new "
        "infrastructure. Persistence alone does not show that it is optimal.",
    ),
    _note(
        27, "philosophy",
        "Convention and coordination. A shared convention can make action "
        "predictable even when another convention could serve the same purpose. "
        "Its usefulness can depend on others continuing to follow it.",
    ),
    _note(
        28, "history",
        "Railway gauges and inherited infrastructure. Decisions about track "
        "standards could shape later connections and conversion costs. Physical "
        "networks make earlier choices consequential for subsequent planners.",
    ),
    _note(
        29, "anthropology",
        "Custom and adaptation. A customary practice can persist while its "
        "meaning changes. Describing it as traditional should not imply that "
        "participants reproduce it unchanged or without debate.",
    ),
    _note(
        30, "education",
        "Curricular inertia. Textbooks, examinations, and teacher preparation "
        "reinforce one another. Revising a syllabus can therefore require changes "
        "to several connected routines, not just a new list of topics.",
    ),
    # Cluster 7: Uncertainty and risk.
    _note(
        31, "politics",
        "Policy under uncertainty. Decisions often precede reliable estimates "
        "of their effects. A reversible pilot can offer a different response "
        "to uncertainty than an immediate, permanent commitment.",
    ),
    _note(
        32, "psychology",
        "Availability and perceived risk. An event that is easy to recall can "
        "feel especially likely. Vivid stories may attract attention even when "
        "they provide little information about the frequency of an outcome.",
    ),
    _note(
        33, "sociology",
        "Unequal exposure to risk. The benefits of an activity and its hazards "
        "may fall on different groups. Public arguments about acceptable risk "
        "can conceal differences in who has the power to refuse it.",
    ),
    _note(
        34, "literature",
        "Suspense and incomplete information. A narrative can make uncertainty "
        "felt by restricting what a character or reader knows. The same event "
        "can appear threatening or ordinary depending on its presentation.",
    ),
    _note(
        35, "science",
        "Uncertainty in measurement. A reported value needs context about "
        "precision and possible error. Additional decimal places do not "
        "necessarily indicate better knowledge of the measured quantity.",
    ),
    # Cluster 8: Inequality and inherited advantage.
    _note(
        36, "economics",
        "Compounding advantage. Access to savings, credit, or secure housing "
        "can make later opportunities easier to pursue. Small initial "
        "differences may accumulate through several reinforcing mechanisms.",
    ),
    _note(
        37, "philosophy",
        "Moral luck and desert. People do not choose all the circumstances "
        "that shape their achievements. This raises questions about how much "
        "reward can be justified by individual merit alone.",
    ),
    _note(
        38, "history",
        "Property qualifications and citizenship. In various historical "
        "systems, political participation depended on wealth or property. "
        "Economic standing could thus help determine access to political influence.",
    ),
    _note(
        39, "anthropology",
        "Inheritance beyond possessions. Families may transmit obligations, "
        "relationships, names, and claims to belonging alongside material "
        "resources. What counts as an inheritance varies across settings.",
    ),
    _note(
        40, "education",
        "Familiarity with academic expectations. Students arrive with different "
        "experience of school language and routines. An assessment may reward "
        "that familiarity alongside the knowledge it intends to measure.",
    ),
    # Cluster 9: Identity and boundaries.
    _note(
        41, "politics",
        "Defining the political community. Citizenship rules draw boundaries "
        "around rights and participation. Debates about inclusion also ask "
        "which relationships should count as grounds for membership.",
    ),
    _note(
        42, "psychology",
        "Social identity and comparison. Group membership can become part of "
        "how people understand themselves. Comparisons between groups may "
        "influence judgments even when the immediate stakes are modest.",
    ),
    _note(
        43, "sociology",
        "Boundary work. Groups distinguish insiders from outsiders through "
        "credentials, tastes, language, or practices. These boundaries may "
        "remain influential even when no formal admission rule exists.",
    ),
    _note(
        44, "literature",
        "Belonging in migration narratives. A character may be treated as "
        "foreign in one setting and changed beyond recognition in another. "
        "Identity emerges through competing expectations rather than a single label.",
    ),
    _note(
        45, "science",
        "Classification and its limits. Scientific categories help organize "
        "observations, but boundary cases can expose weaknesses in a scheme. "
        "A useful label is not a guarantee of uniformity among its members.",
    ),
    # Cluster 10: Incentives and unintended consequences.
    _note(
        46, "economics",
        "Incentives and substitution. Rewarding one measurable activity can "
        "shift effort away from another. A rise in the rewarded metric may "
        "therefore coexist with little improvement in the broader objective.",
    ),
    _note(
        47, "philosophy",
        "Intention and foreseeable effects. Evaluating an action may require "
        "distinguishing what an agent sought from what the agent expected "
        "would also happen. Good intentions do not settle every moral question.",
    ),
    _note(
        48, "history",
        "Prohibition and illicit markets. Restrictions on alcohol in the "
        "United States created opportunities for illegal supply. This episode "
        "illustrates how regulation can change an activity's organization.",
    ),
    _note(
        49, "anthropology",
        "Payments and the meaning of participation. Introducing money into "
        "a reciprocal activity may change how participants interpret it. "
        "A payment can signal employment, compensation, or an inappropriate exchange.",
    ),
    _note(
        50, "education",
        "Teaching to the test. When examination results carry strong rewards, "
        "instruction may narrow toward assessed tasks. Better scores need "
        "interpretation in relation to what students can transfer beyond the test.",
    ),
    # Cluster 11: Attention and public agendas.
    _note(
        51, "politics",
        "Agenda setting. Political influence includes shaping which problems "
        "receive discussion. An issue kept off the agenda may never reach "
        "the stage where competing proposals receive a public vote.",
    ),
    _note(
        52, "psychology",
        "Selective attention. People process only part of the information "
        "available at a given moment. Goals and salient signals help determine "
        "what is noticed and what passes without conscious consideration.",
    ),
    _note(
        53, "sociology",
        "Visibility and social recognition. Some kinds of work attract public "
        "credit while others remain background conditions. Visibility is "
        "shaped by institutions as well as by the effort involved.",
    ),
    _note(
        54, "literature",
        "Narrative focalization. A story's chosen perspective directs attention "
        "toward some experiences and away from others. Retelling an episode "
        "through a minor character can change its apparent center of importance.",
    ),
    _note(
        55, "science",
        "Instruments and observability. A detector makes certain phenomena "
        "available for study while remaining insensitive to others. Failure "
        "to observe a signal must be interpreted alongside detection limits.",
    ),
    # Cluster 12: Commons and collective action.
    _note(
        56, "economics",
        "Common-pool resources. When exclusion is difficult and use reduces "
        "what remains for others, individual incentives can threaten a shared "
        "resource. Local rules and monitoring may help coordinate restraint.",
    ),
    _note(
        57, "philosophy",
        "Fairness in shared burdens. Benefiting from a cooperative practice "
        "while refusing its costs raises a question of fair contribution. "
        "Disagreement can concern both the burden and who consented to it.",
    ),
    _note(
        58, "history",
        "Historical irrigation arrangements. Communities managing shared water "
        "have used schedules, maintenance duties, and dispute procedures. "
        "Cooperation depended on practical institutions rather than goodwill alone.",
    ),
    _note(
        59, "anthropology",
        "Commons as social relationships. Shared access to land can involve "
        "specific rights and obligations. Calling land communal need not "
        "mean that anyone may use it without restrictions.",
    ),
    _note(
        60, "education",
        "Group projects and shared responsibility. Uneven contributions can "
        "undermine collaboration. Clear roles and opportunities to discuss "
        "progress may help students coordinate work and recognize hidden effort.",
    ),
    # Cluster 13: Change and resistance.
    _note(
        61, "politics",
        "Reform and organized opposition. A policy's benefits may be widely "
        "dispersed while its costs fall on a small organized group. Political "
        "resistance can depend on this distribution, not only on total effects.",
    ),
    _note(
        62, "psychology",
        "Status quo bias. An existing arrangement can receive extra weight "
        "simply because it is the current one. Uncertainty about change and "
        "anticipated regret can reinforce a preference for staying put.",
    ),
    _note(
        63, "sociology",
        "Organizational routines. Repeated procedures reduce the effort needed "
        "for coordination. They can also make an organization slow to respond "
        "when circumstances no longer match its familiar assumptions.",
    ),
    _note(
        64, "literature",
        "Change in Chekhov's The Cherry Orchard. The threatened sale of an "
        "estate brings economic pressure into conflict with attachment to "
        "a familiar world. Characters respond unevenly to the prospect of transition.",
    ),
    _note(
        65, "science",
        "Revising a scientific framework. An anomaly may motivate a local "
        "correction or a broader reconsideration. Deciding between them "
        "requires judging both the evidence and the alternatives available.",
    ),
    # Cluster 14: Measurement and value.
    _note(
        66, "economics",
        "GDP and well-being. Recorded economic production does not capture "
        "every aspect of a good life. Distribution, unpaid activity, and "
        "environmental conditions complicate its interpretation as a welfare measure.",
    ),
    _note(
        67, "philosophy",
        "Plural values. Friendship, freedom, knowledge, and comfort may all "
        "matter without fitting neatly onto a single scale. A numerical "
        "ranking can conceal judgments about how these goods should be compared.",
    ),
    _note(
        68, "history",
        "Censuses and administrative categories. Counting a population requires "
        "decisions about households, occupations, and membership. Historical "
        "statistics reflect administrative purposes as well as recorded lives.",
    ),
    _note(
        69, "anthropology",
        "Different measures of wealth. Livestock, land, ceremonial objects, "
        "or dependable relationships may carry distinct forms of value. "
        "Translating them into one monetary figure can lose important meanings.",
    ),
    _note(
        70, "education",
        "Grades as compressed judgments. A grade combines performance into "
        "a convenient signal. It may obscure whether a learner struggles "
        "with understanding, expression, preparation, or the assessment format.",
    ),
    # Cluster 15: Stories and explanation.
    _note(
        71, "politics",
        "Political narratives of crisis. Describing a situation as a crisis "
        "can make some responses appear urgent and others irresponsible. "
        "The framing links an account of causes to a preferred course of action.",
    ),
    _note(
        72, "psychology",
        "Hindsight and coherent stories. Once an outcome is known, earlier "
        "events can appear to point toward it more clearly than they did "
        "at the time. A satisfying explanation may understate past uncertainty.",
    ),
    _note(
        73, "sociology",
        "Institutional origin stories. Organizations tell stories about their "
        "founding to explain present commitments. These accounts can select "
        "continuity and shared purpose from a more contested history.",
    ),
    _note(
        74, "literature",
        "Unreliable narration. A narrator's explanation may conflict with "
        "details the reader notices. The resulting gap invites attention "
        "to perspective, self-justification, and the limits of a coherent story.",
    ),
    _note(
        75, "science",
        "Mechanism and plausible explanation. A proposed mechanism can make "
        "a result intelligible, but plausibility alone does not establish "
        "that it caused the observation. Competing explanations need discriminating evidence.",
    ),
    # Cluster 16: Networks and diffusion.
    _note(
        76, "economics",
        "Network effects. A service may become more useful as more people "
        "adopt it. This can encourage concentration even when users would "
        "prefer some features of a smaller competing service.",
    ),
    _note(
        77, "philosophy",
        "Testimony and dependent evidence. Hearing a claim from several "
        "people is less informative if they all repeat one source. The "
        "number of voices and the independence of their reasons are different matters.",
    ),
    _note(
        78, "history",
        "Print networks and the Reformation. Pamphlets and printers helped "
        "religious arguments circulate across parts of Europe. Their effects "
        "also depended on literacy, local politics, and existing social connections.",
    ),
    _note(
        79, "anthropology",
        "Cultural borrowing and reinterpretation. A practice can change "
        "meaning as it moves between communities. Diffusion involves local "
        "selection and adaptation rather than the transfer of an unchanged package.",
    ),
    _note(
        80, "education",
        "Ideas spreading through teacher networks. Colleagues can share "
        "classroom techniques through trusted relationships. A practice's "
        "popularity may reflect accessibility and social ties as well as its effectiveness.",
    ),
    # Cluster 17: Surveillance and self-regulation.
    _note(
        81, "politics",
        "Surveillance and participation. The possibility of being monitored "
        "can affect whether people attend a meeting or express a view. "
        "Power may operate through anticipated observation without direct intervention.",
    ),
    _note(
        82, "psychology",
        "Behavior under observation. People may change their conduct when "
        "they believe someone is watching. Concern about evaluation can "
        "influence both deliberate presentation and willingness to experiment.",
    ),
    _note(
        83, "sociology",
        "Internalized discipline. Repeated monitoring can encourage people "
        "to supervise their own behavior against an expected standard. "
        "The observer need not be visibly present for the expectation to matter.",
    ),
    _note(
        84, "literature",
        "Surveillance in Orwell's Nineteen Eighty-Four. Uncertainty about "
        "observation shapes private conduct as well as public speech. The "
        "novel connects political control with the erosion of spaces for independent thought.",
    ),
    _note(
        85, "science",
        "Measurement reactivity in human research. Collecting observations "
        "can alter the behavior under study. A research design should consider "
        "whether participants respond to the measurement process itself.",
    ),
    # Cluster 18: Time horizons and future obligations.
    _note(
        86, "economics",
        "Discounting future outcomes. Giving less weight to distant benefits "
        "can change which investments appear worthwhile. Long-term environmental "
        "decisions can be sensitive to assumptions about that weighting.",
    ),
    _note(
        87, "philosophy",
        "Obligations to future people. People who will live later cannot "
        "participate in present decisions. Their absence raises questions "
        "about representation, responsibility, and acceptable long-term harm.",
    ),
    _note(
        88, "history",
        "Cathedral construction across generations. Some major building "
        "projects extended beyond the lives of their initial patrons and "
        "workers. Their continuation depended on institutions that could renew commitments.",
    ),
    _note(
        89, "anthropology",
        "Ancestry and intergenerational responsibility. Some accounts of "
        "landholding emphasize obligations to predecessors and descendants. "
        "Present use can be understood as stewardship within a longer relationship.",
    ),
    _note(
        90, "education",
        "Immediate performance and durable learning. A lesson that feels "
        "fluent today may not produce lasting recall. Evaluating learning "
        "after a delay can reveal a different picture from immediate success.",
    ),
    # Cluster 19: Polarization and disagreement.
    _note(
        91, "politics",
        "Polarization and compromise. When political opponents are viewed "
        "as threats to a group's identity, compromise can look like betrayal. "
        "Institutional incentives and social interpretation can reinforce each other.",
    ),
    _note(
        92, "psychology",
        "Motivated evaluation of evidence. People can scrutinize unwelcome "
        "claims more harshly than congenial ones. A disagreement may persist "
        "even when both sides receive the same information.",
    ),
    _note(
        93, "sociology",
        "Homophily and separated conversations. Relationships often form "
        "among people who share traits or outlooks. This can limit encounters "
        "with different experiences without requiring a deliberate refusal to listen.",
    ),
    _note(
        94, "literature",
        "Multiple voices in the novel. A narrative can present competing "
        "worldviews without resolving them into one authoritative judgment. "
        "Readers must consider how each voice makes sense from its own position.",
    ),
    _note(
        95, "science",
        "Adversarial collaboration. Researchers with competing explanations "
        "can agree on a study intended to distinguish them. Shared criteria "
        "for interpreting results make disagreement more productive.",
    ),
    # Cluster 20: Resilience and diversity.
    _note(
        96, "economics",
        "Diversification and shared shocks. Spreading investments can reduce "
        "exposure to an individual failure. Protection is weaker when apparently "
        "different investments depend on the same underlying conditions.",
    ),
    _note(
        97, "philosophy",
        "Pluralism and fallibility. Allowing different ways of living can "
        "reflect recognition that no single perspective settles every question. "
        "Pluralism still requires ways to address conflicts between commitments.",
    ),
    _note(
        98, "history",
        "The Irish potato famine and vulnerability. Dependence on potatoes "
        "among many poor households made crop disease devastating. Landholding, "
        "poverty, and political responses also shaped the scale of suffering.",
    ),
    _note(
        99, "anthropology",
        "Livelihood diversity. Households may combine farming, wage work, "
        "exchange, and migration to manage uncertainty. Several activities "
        "can provide flexibility, though they may remain exposed to common shocks.",
    ),
    _note(
        100, "education",
        "Multiple representations in teaching. Explaining an idea through "
        "words, diagrams, and examples can offer complementary routes to "
        "understanding. The representations help most when their connections are explicit.",
    ),
]
