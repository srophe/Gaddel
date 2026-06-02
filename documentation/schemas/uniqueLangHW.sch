<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron" xmlns:sqf="http://www.schematron-quickfix.com/validator/process" queryBinding="xslt2">
    <sch:ns uri="http://www.tei-c.org/ns/1.0" prefix="tei"/>
    <sch:ns uri="https://srophe.app" prefix="srophe"/>
    <sch:pattern>
        
        
        <!-- This standalone Schematron file is preferable to Schematron embedded in ODD because it allows XPath 2.0 -->
        
        <sch:rule context="tei:body/tei:listPerson/tei:person">
            
            <sch:assert test="
                every $lang in distinct-values(
                for $l in tei:persName/@xml:lang
                return substring-before(concat($l, '-'), '-')
                )
                satisfies count(
                tei:persName[
                substring-before(concat(@xml:lang, '-'), '-') = $lang
                and
                contains(concat(' ', @srophe:tags, ' '), ' #syriaca-headword ')
                ]
                ) &lt;= 1
                ">
                Only one &gt;persName&lt; with @srophe:tags '#syriaca-headword' is allowed per base xml:lang.
            </sch:assert>
            
        </sch:rule>
        
        
        
        <sch:rule context="tei:body/tei:listPlace/tei:place">
            
            <sch:assert test="
                every $lang in distinct-values(
                for $l in tei:placeName/@xml:lang
                return substring-before(concat($l, '-'), '-')
                )
                satisfies count(
                tei:placeName[
                substring-before(concat(@xml:lang, '-'), '-') = $lang
                and
                contains(concat(' ', @srophe:tags, ' '), ' #syriaca-headword ')
                ]
                ) &lt;= 1
                ">
                Only one &lt;placeName&gt; with @srophe:tags '#syriaca-headword' is allowed per base xml:lang.
            </sch:assert>
            
        </sch:rule>
        
        
        
        <sch:rule context="tei:body/tei:bibl">
            
            <sch:assert test="
                every $lang in distinct-values(
                for $l in tei:title/@xml:lang
                return substring-before(concat($l, '-'), '-')
                )
                satisfies count(
                tei:title[
                substring-before(concat(@xml:lang, '-'), '-') = $lang
                and
                contains(concat(' ', @srophe:tags, ' '), ' #syriaca-headword ')
                ]
                ) &lt;= 1
                ">
                Only one &gt;persName&lt; with @srophe:tags '#syriaca-headword' is allowed per base xml:lang.
            </sch:assert>
            
        </sch:rule>
        
        
        
        <!--<sch:rule context="//tei:text//tei:place/tei:placeName[contains(@srophe:tags, 'syriaca-headword')]">
            <sch:report test=".[contains(@xml:lang, 'en')]/following-sibling::tei:placeName[contains(@xml:lang, 'en')][contains(@srophe:tags, '#syriaca-headword')]">
                There must be one and only one &lt;placeName&gt; element with the combination of @srophe:tags="#syriaca-headword" and @xml:lang="en".
            </sch:report>
        </sch:rule>-->
        
        <!--<sch:rule context="//tei:text//tei:place/tei:placeName[@srophe:tags='#syriaca-headword']">
            <sch:let name="langsOfHW" value="//tei:place/tei:placeName[contains(@srophe:tags, '#syriaca-headword')]/@xml:lang"/>
            <sch:assert test="count(distinct-values($langsOfHW)) = count($langsOfHW)">
                There cannot be more than one headword (@srophe:tags="#syriaca-headword") per &lt;placeName&gt; with the same language (@xml:lang).
            </sch:assert>
        </sch:rule>-->
        
        <!--<sch:rule context="//tei:text//tei:person/tei:persName[contains(@srophe:tags, 'syriaca-headword')]">
            <sch:report test=".[contains(@xml:lang, 'en')]/following-sibling::tei:persName[contains(@xml:lang, 'en')][contains(@srophe:tags, '#syriaca-headword')]">
                There must be one and only one &lt;persName&gt; element with the combination of @srophe:tags="#syriaca-headword" and @xml:lang="en".
            </sch:report>
        </sch:rule>-->
        
        <!--<sch:rule context="//tei:text//tei:person/tei:persName[@srophe:tags='#syriaca-headword']">
            <sch:let name="langsOfHW" value="//tei:person/tei:persName[contains(@srophe:tags, '#syriaca-headword')]/@xml:lang"/>
            <sch:assert test="count(distinct-values($langsOfHW)) = count($langsOfHW)">
                There cannot be more than one headword (@srophe:tags="#syriaca-headword") per &lt;persName&gt; with the same language (@xml:lang).
            </sch:assert>
        </sch:rule>-->
        
        
        
        
    </sch:pattern>
</sch:schema>