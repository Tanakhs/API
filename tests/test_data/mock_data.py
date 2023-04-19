def mock_chapter_data():
    return mock_chapters_data()[0]


def mock_chapters_data():
    return [
        {
            "_id": "63dc389d0bb56cd596d575b9",
            "author": "Eli Entelis",
            "holy_book": 1,
            "chapter_number": 1,
            "tags": [
                "dfgdfg",
                "sdfsdf"
            ],
            "book": "בראשית",
            "verses": [
                "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the "
                "industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type "
                "and scrambled it to make a type specimen book. It has survived not only five centuries, but also the "
                "leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s "
                "with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop "
                "publishing software like Aldus PageMaker including versions of Lorem Ipsum."
            ],
            "summary": "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has "
                       "been the industry's standard dummy text ever since the 1500s, when an unknown printer took a "
                       "galley of type and scrambled it to make a type specimen book. It has survived not only five "
                       "centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It "
                       "was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum "
                       "passages, and more recently with desktop publishing software like Aldus PageMaker including "
                       "versions of Lorem Ipsum.",
            "analysis": "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has "
                        "been the industry's standard dummy text ever since the 1500s, when an unknown printer took a "
                        "galley of type and scrambled it to make a type specimen book. It has survived not only five "
                        "centuries, but also the leap into electronic typesetting, remaining essentially unchanged. "
                        "It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum "
                        "passages, and more recently with desktop publishing software like Aldus PageMaker including "
                        "versions of Lorem Ipsum.",
            "rating": {
                "moral": 3,
                "scientific": 2,
                "historical": 2
            },
            "parentComments": [
                ""
            ],
            "chapter_letters": "א",
            "title": "ויהי אור",
            "comments": [
                {
                    "_id": "63dbfcf7e8b3b669de1065b9",
                    "name": "test user",
                    "picture": "https://www.shutterstock.com/image-vector/man-icon-vector-260nw-1040084344.jpg",
                    "content": "i am the best",
                    "date_added": "2023-02-02T20:12:06.073+00:00",
                    "date_updated": "2023-02-02T20:12:06.073+00:00"
                },
                {
                    "_id": "63dd44a355621619543757c0",
                    "name": "test user",
                    "picture": "https://www.shutterstock.com/image-vector/man-icon-vector-260nw-1040084344.jpg",
                    "content": "i am the best",
                    "date_added": "2023-02-02T20:12:06.073+00:00",
                    "date_updated": "2023-02-02T20:12:06.073+00:00"
                }
            ]
        }
    ]


def mock_comment_data():
    return {
        "_id": "63dd81295f249633483d6e21",
        "name": "test",
        "picture": "https://www.shutterstock.com/image-vector/man-icon-vector-260nw-1040084344.jpg",
        "content": "updated2",
        "date_added": "2023-02-03T18:50:54.242+00:00",
        "date_updated": "2023-02-03T18:50:54.242+00:00"
    }
