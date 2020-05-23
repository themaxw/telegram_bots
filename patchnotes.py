import requests
from bs4 import BeautifulSoup

baseUrl = "https://euw.leagueoflegends.com"
patchNotesIndexUrl = baseUrl + "/en-gb/news/tags/patch-notes"


def getLatestNotes():
    indexHtml = requests.get(patchNotesIndexUrl).content

    index = BeautifulSoup(indexHtml, 'html.parser')
    notes = index.find('li')
    if notes is not None:
        notes = notes.find('a')
        link = notes.attrs['href']
        return baseUrl + link


def parsePatchNotes(patchNotesUrl):

    patchNotesHtml = requests.get(patchNotesUrl).content
    soup = BeautifulSoup(patchNotesHtml, 'html.parser')
    content = soup.find('div', {"id": "patch-notes-container"})

    summary = content.find('blockquote', {'class': 'blockquote context'})

    alleChanges = soup.findAll('div', {'class': 'content-border'})
    changes = {}

    for c in alleChanges:
        title = c.find('h3')
        if title is not None:
            if 'class' in title.attrs and title.attrs['class'] == 'change-title':
                title = title.find('a').text

            else:
                title = title.text

            if title != 'Related Content':
                changes[title] = {}
        else:
            continue

        changeSummary = c.find('p', {'class': 'summary'})
        if changeSummary is not None:
            changeSummary = changeSummary.text
            changes[title]['summary'] = changeSummary

        description = c.find('blockquote')
        if description is not None:
            changes[title]['description'] = description.text

        spells = c.findAll('h4')
        if len(spells):
            spellsTemp = []
            for spell in spells:
                spellChange = {'name': spell.text, 'changes': []}
                nextLine = spell.nextSibling
                while nextLine != '<hr class="divider"/>' and nextLine is not None:
                    if nextLine == '\n':
                        nextLine = nextLine.nextSibling
                        continue
                    elif 'class' in nextLine.attrs and 'divider' in nextLine.attrs['class']:
                        break
                    #attributeChange = nextLine.find('div', {'class' : 'attribute-change'})
                    attributeChange = nextLine
                    spellChange['changes'].append(attributeChange.text)
                    nextLine = nextLine.nextSibling
                spellsTemp.append(spellChange)
            if len(spellsTemp):
                changes[title]['spells'] = spellsTemp

    return changes


def getChanges():
    url = getLatestNotes()
    changes = parsePatchNotes(url)
    return changes


if __name__ == "__main__":
    url = getLatestNotes()
    print(patchNotesIndexUrl)
    changes = parsePatchNotes(url)
    print(changes['Soraka'])
