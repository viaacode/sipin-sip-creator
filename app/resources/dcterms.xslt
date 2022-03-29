<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:premis="http://www.loc.gov/premis/v3" xmlns:ebu="urn:ebu:metadata-schema:ebuCore_2012" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:viaa="http://www.vrt.be/mig/viaa/api" xsi:schemaLocation="urn:ebu:metadata-schema:ebucore https://www.ebu.ch/metadata/schemas/EBUCore/20171009/ebucore.xsd" version="1.1">
    <xsl:output method="xml" encoding="UTF-8" indent="yes" />
    <xsl:template match="//VIAA">
        <premis:object>
            <!-- Title -->
            <dcterms:title>
                <xsl:value-of select="dc_title" />
            </dcterms:title>

            <!-- Description -->
            <dcterms:description>
                <xsl:value-of select="dc_description" />
            </dcterms:description>

            <!-- Identifier -->
            <dcterms:identifier>
                <xsl:value-of select="dc_identifier_localid" />
            </dcterms:identifier>

            <!-- Identifiers -->
            <xsl:for-each select="dc_identifier_localids/*">
                <premis:objectIdentifier xmlns:premis="http://www.loc.gov/premis/v3">
                    <premis:objectIdentifierType><xsl:value-of select="name()" /></premis:objectIdentifierType>
                    <premis:objectIdentifierValue><xsl:value-of select="text()" /></premis:objectIdentifierValue>
                </premis:objectIdentifier>
            </xsl:for-each>

            <!-- Types -->
            <xsl:for-each select="dc_types/multiselect">
                <dcterms:type>
                    <xsl:value-of select="text()" />
                </dcterms:type>
            </xsl:for-each>

            <!-- Created -->
            <dcterms:created xsi:type="edtf">
                <xsl:value-of select="dcterms_created" />
            </dcterms:created>

            <!-- Issued -->
            <dcterms:issued xsi:type="edtf">
                <xsl:value-of select="dcterms_issued" />
            </dcterms:issued>

            <!-- Coverages (ruimte) -->
            <xsl:for-each select="dc_coverages/ruimte">
                <dcterms:spatial>
                    <xsl:value-of select="text()" />
                </dcterms:spatial>
            </xsl:for-each>

            <!-- Subjects -->
            <xsl:for-each select="dc_subjects/Trefwoord">
                <dcterms:subject><xsl:value-of select="text()" /></dcterms:subject>
            </xsl:for-each>

            <!-- Rights -->
            <xsl:for-each select="dc_rights_licenses/multiselect">
                <dcterms:rights><xsl:value-of select="text()" /></dcterms:rights>
            </xsl:for-each>
        </premis:object>
    </xsl:template>
</xsl:stylesheet>