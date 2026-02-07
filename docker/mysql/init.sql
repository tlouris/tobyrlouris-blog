-- MySQL Initialization Script for Technology Innovations Blog
-- This script creates tables and populates initial data

USE visitor_log;

-- Tables are created by SQLAlchemy, but we'll add indexes and sample data

-- Create admin_sessions table
CREATE TABLE IF NOT EXISTS admin_sessions (
    id VARCHAR(64) PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    expires_at DATETIME NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT
);

-- Create login_attempts table
CREATE TABLE IF NOT EXISTS login_attempts (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    ip_address VARCHAR(45) NOT NULL,
    attempted_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    success BOOLEAN DEFAULT FALSE NOT NULL,
    INDEX idx_ip_attempted (ip_address, attempted_at)
);

-- Insert sample blog posts (uses status column instead of published)
INSERT INTO blog_posts (slug, title, excerpt, content, category, featured, status, reading_time, created_at) VALUES
(
    'digital-transformation-roadmap-wastewater',
    'Digital Transformation in Wastewater Treatment: A Strategic Roadmap',
    'Exploring how digital technologies are revolutionizing wastewater treatment operations and creating new opportunities for efficiency and sustainability.',
    '<p>The wastewater industry stands at a critical junction. Legacy systems that have served reliably for decades now face increasing demands for efficiency, sustainability, and resilience.</p><p>Digital transformation offers a path forward, but success requires more than just technology adoption—it demands a strategic approach that addresses organizational readiness, change management, and sustainable implementation.</p><h2>Understanding the Current State</h2><p>Most wastewater utilities operate with a mix of modern and legacy systems. SCADA systems may be decades old, while newer IoT sensors provide real-time data that existing infrastructure cannot fully leverage. This creates both challenges and opportunities.</p><h2>Building Your Roadmap</h2><p>A successful digital transformation roadmap should address three key areas: assessment, prioritization, and execution. Begin with a thorough evaluation of current capabilities, identify quick wins that demonstrate value, and build toward larger, more transformative initiatives.</p>',
    'Digital Strategy',
    TRUE,
    'published',
    '8 min read',
    '2025-01-15 10:00:00'
),
(
    'scada-security-best-practices',
    'Protecting Critical Water Infrastructure: SCADA Security Best Practices',
    'Best practices for securing SCADA systems and operational technology in wastewater facilities against emerging cyber risks and threats.',
    '<p>As wastewater facilities become more connected and digitized, they also become more vulnerable to cyber threats. SCADA systems that were once isolated now face sophisticated attacks that can disrupt operations and compromise safety.</p><h2>The Threat Landscape</h2><p>Cyber threats targeting water utilities have increased dramatically in recent years. From ransomware attacks to nation-state actors targeting critical infrastructure, the risks are real and growing.</p><h2>Defense in Depth</h2><p>Effective SCADA security requires a layered approach. This includes network segmentation, access controls, continuous monitoring, incident response planning, and regular security assessments.</p><p>However, security cannot come at the expense of operations. The challenge is implementing robust protections while maintaining the reliability and availability that wastewater operations demand.</p>',
    'Cybersecurity & Resilience',
    FALSE,
    'published',
    '7 min read',
    '2025-01-12 14:30:00'
),
(
    'lessons-scada-upgrade-project',
    'Lessons from a Major SCADA System Upgrade: What Worked and What Didn''t',
    'Key insights and practical lessons learned from implementing a modern SCADA system at a regional wastewater treatment plant.',
    '<p>Upgrading a critical SCADA system while maintaining 24/7 operations is one of the most challenging projects a wastewater utility can undertake. Here are the lessons we learned from a recent major upgrade.</p><h2>Planning Phase Success Factors</h2><p>The projects that succeed share common characteristics: executive support, clear objectives, realistic timelines, and extensive stakeholder engagement. Our planning phase took longer than anticipated, but the extra time paid dividends during implementation.</p><h2>What Went Well</h2><p>Phased implementation allowed us to validate each component before proceeding. Operator training started early and continued throughout the project. Vendor relationships were collaborative rather than adversarial.</p><h2>Challenges We Faced</h2><p>Integration with legacy systems proved more complex than expected. Some vendor commitments did not materialize. Change management required more attention than initially allocated. Budget pressures created difficult tradeoff decisions.</p>',
    'Project Lessons',
    FALSE,
    'published',
    '10 min read',
    '2025-01-08 09:15:00'
),
(
    'epa-cybersecurity-requirements-2025',
    'EPA Cybersecurity Requirements: Compliance Roadmap for Water Utilities',
    'Understanding new federal regulations for cybersecurity in water and wastewater utilities and how to achieve and maintain compliance.',
    '<p>New EPA cybersecurity requirements are reshaping how water and wastewater utilities approach operational technology security. Understanding these requirements and building a compliance roadmap is now a critical priority.</p><h2>Regulatory Overview</h2><p>The America''s Water Infrastructure Act (AWIA) requires community water systems serving more than 3,300 people to conduct risk and resilience assessments and develop emergency response plans that specifically address cybersecurity.</p><h2>Key Requirements</h2><p>Utilities must assess cybersecurity risks to their systems, develop incident response plans, implement security controls, and maintain documentation of compliance efforts. The requirements are performance-based rather than prescriptive, giving utilities flexibility in implementation.</p><h2>Building Your Compliance Roadmap</h2><p>Start with a gap assessment against current requirements. Develop a phased implementation plan. Engage stakeholders early. Document everything. Regular testing and updates are essential—compliance is not a one-time project but an ongoing program.</p>',
    'Industry Trends & Regulation',
    FALSE,
    'published',
    '6 min read',
    '2025-01-05 11:00:00'
),
(
    'iot-sensors-water-quality-monitoring',
    'IoT Sensors: The Future of Real-Time Water Quality Monitoring',
    'How Internet of Things technology is enabling real-time monitoring, predictive analytics, and smarter decision-making in wastewater systems.',
    '<p>Internet of Things (IoT) sensors are transforming water quality monitoring from periodic sampling to continuous, real-time analysis. This shift enables faster responses to issues, better compliance, and more efficient operations.</p><h2>Technology Overview</h2><p>Modern IoT sensors can monitor dozens of parameters continuously and transmit data wirelessly to central systems. Edge computing allows for local processing and intelligent alarming, reducing false positives and improving operator efficiency.</p><h2>Implementation Considerations</h2><p>Successful IoT deployments require careful sensor selection, robust network infrastructure, data management strategies, and integration with existing SCADA and laboratory information systems.</p><p>Security is paramount—each connected sensor is a potential attack vector. Network segmentation, encryption, and continuous monitoring are essential components of any IoT deployment.</p>',
    'Digital Strategy',
    FALSE,
    'published',
    '7 min read',
    '2024-12-20 13:45:00'
),
(
    'cyber-resilience-small-water-systems',
    'Building Cyber Resilience in Small Water Systems on Limited Budgets',
    'Practical, budget-conscious approaches to cybersecurity for smaller wastewater treatment facilities and utilities.',
    '<p>Small water systems face the same cyber threats as large utilities but typically have limited budgets and staff. However, effective cybersecurity doesn''t always require significant investment—it requires strategic thinking and proper prioritization.</p><h2>Starting Points</h2><p>Begin with basic cyber hygiene: strong passwords, regular patching, backups, and access controls. These fundamentals are free or low-cost but provide substantial risk reduction.</p><h2>Leveraging Resources</h2><p>Many resources are available to small systems at no cost: EPA cybersecurity guides, WaterISAC membership, state programs, and mutual aid agreements with neighboring utilities. Don''t try to solve every problem alone.</p><h2>Building Capabilities Over Time</h2><p>Cyber resilience is a journey, not a destination. Start with the basics, document your efforts, learn from incidents, and incrementally improve your security posture as resources allow.</p>',
    'Cybersecurity & Resilience',
    FALSE,
    'published',
    '8 min read',
    '2024-12-15 10:30:00'
),
(
    'it-ot-convergence-challenges',
    'IT/OT Convergence: Bridging the Gap in Wastewater Operations',
    'Navigating the technical and organizational challenges of converging information technology and operational technology systems.',
    '<p>The convergence of IT and OT systems promises significant benefits but also introduces new complexities and risks. Successfully bridging this gap requires understanding both the technical and cultural dimensions of convergence.</p><h2>Understanding the Divide</h2><p>IT and OT teams have historically operated with different priorities, timelines, and risk tolerances. IT focuses on confidentiality and data protection, while OT prioritizes availability and safety. Convergence requires reconciling these different perspectives.</p><h2>Technical Integration</h2><p>Modern architectures enable OT systems to leverage IT capabilities—cloud computing, advanced analytics, remote access—while maintaining operational reliability. However, integration must be carefully planned and implemented.</p><h2>Organizational Change</h2><p>Technical integration is often easier than organizational change. Breaking down silos, establishing shared governance, and building mutual understanding between IT and OT teams are critical success factors.</p>',
    'Project Lessons',
    FALSE,
    'published',
    '9 min read',
    '2024-12-10 14:00:00'
),
(
    'data-analytics-wastewater-optimization',
    'Leveraging Data Analytics for Wastewater Treatment Optimization',
    'How advanced analytics and machine learning are helping utilities optimize treatment processes, reduce costs, and improve outcomes.',
    '<p>The wastewater industry generates massive amounts of data, but historically much of this data has gone unused. Advanced analytics and machine learning are changing this, enabling utilities to extract actionable insights from their data and optimize operations.</p><h2>From Data to Insights</h2><p>Modern data platforms can aggregate information from SCADA systems, laboratory analyses, maintenance records, and external sources to provide comprehensive operational visibility. However, data alone is not enough—it must be transformed into actionable insights.</p><h2>Optimization Opportunities</h2><p>Analytics can optimize chemical dosing, predict equipment failures, improve energy efficiency, enhance compliance, and support better decision-making. The opportunities are significant, but require both technology and expertise to realize.</p><h2>Implementation Approach</h2><p>Start with specific use cases that have clear value. Build data infrastructure incrementally. Invest in staff training. Partner with experts where internal capabilities are limited. Focus on sustainable solutions that your team can maintain long-term.</p>',
    'Industry Trends & Regulation',
    FALSE,
    'published',
    '8 min read',
    '2024-12-05 09:00:00'
);

-- Grant permissions
GRANT ALL PRIVILEGES ON visitor_log.* TO 'visitor_log_user'@'%';
FLUSH PRIVILEGES;
