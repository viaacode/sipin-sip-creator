<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:premis="http://www.loc.gov/premis/v3" xmlns:ebu="urn:ebu:metadata-schema:ebuCore_2012" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:viaa="http://www.vrt.be/mig/viaa/api" xsi:schemaLocation="urn:ebu:metadata-schema:ebucore https://www.ebu.ch/metadata/schemas/EBUCore/20171009/ebucore.xsd" version="1.1">
    <xsl:output method="xml" encoding="UTF-8" indent="yes" />
    <xsl:template match="VIAA">
        <premis:object>
            <xsl:apply-templates select="*" />
        </premis:object>
    </xsl:template>

    <!-- Identifier -->
    <xsl:template match="dc_identifier_localid">
        <xsl:element name="dcterms:identifier">
            <xsl:value-of select="." />
        </xsl:element>
    </xsl:template>

    <!-- Identifiers -->
    <xsl:template match="dc_identifier_localids">
        <xsl:for-each select="*">
            <xsl:element name="premis:objectIdentifier">
                <xsl:element name="premis:objectIdentifierType">
                    <xsl:value-of select="name()" />
                </xsl:element>
                <xsl:element name="premis:objectIdentifierValue">
                    <xsl:value-of select="text()" />
                </xsl:element>
            </xsl:element>
        </xsl:for-each>
    </xsl:template>

    <!-- Created -->
    <xsl:template match="dcterms_created">
        <xsl:element name="dcterms:created">
            <xsl:attribute name="xsi:type">
                <xsl:text>edtf</xsl:text>
            </xsl:attribute>
            <xsl:value-of select="." />
        </xsl:element>
    </xsl:template>

    <!-- Issued -->
    <xsl:template match="dcterms_issued">
        <xsl:element name="dcterms:issued">
            <xsl:attribute name="xsi:type">
                <xsl:text>edtf</xsl:text>
            </xsl:attribute>
            <xsl:value-of select="." />
        </xsl:element>
    </xsl:template>

    <!-- Title -->
    <xsl:template match="dc_title">
        <xsl:element name="dcterms:title">
            <xsl:value-of select="." />
        </xsl:element>
    </xsl:template>

    <!-- Description -->
    <xsl:template match="dc_description">
        <xsl:element name="dcterms:description">
            <xsl:value-of select="." />
        </xsl:element>
    </xsl:template>

    <!-- Types -->
    <xsl:template match="dc_types/multiselect">
        <xsl:element name="dcterms:type">
            <xsl:value-of select="text()" />
        </xsl:element>
    </xsl:template>

    <!-- Coverages (ruimte) -->
    <xsl:template match="dc_coverages/ruimte">
        <xsl:element name="dcterms:spatial">
            <xsl:value-of select="text()" />
        </xsl:element>
    </xsl:template>

    <!-- Subjects -->
    <xsl:template match="dc_subjects/Trefwoord">
        <xsl:element name="dcterms:subject">
            <xsl:value-of select="text()" />
        </xsl:element>
    </xsl:template>

    <!-- Rights -->
    <xsl:template match="dc_rights_licenses/multiselect">
        <xsl:element name="dcterms:rights">
            <xsl:value-of select="text()" />
        </xsl:element>
    </xsl:template>

    <xsl:template match="@*|node()">
        <xsl:apply-templates select="node()" />
    </xsl:template>
</xsl:stylesheet>