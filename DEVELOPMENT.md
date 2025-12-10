# Development Guide - Faberlic Satire RAG

## Project Overview

Faberlic Satire RAG is a content generation and distribution system that combines satirical writing with Retrieval-Augmented Generation (RAG) technology for creating engaging content.

## Architecture

### Directory Structure

```
faberlic-satire-rag/
├── .github/workflows/      # CI/CD pipeline configuration
│   └── ci-cd.yml          # GitHub Actions workflow
├── content/               # Generated content files
│   ├── week1/            # Week 1 satirical stories
│   ├── week2/            # Week 2 satirical stories
│   └── week3/            # Week 3 satirical stories
├── analytics/            # Analytics and tracking
├── data/                 # Data files and configurations
├── docs/                 # Documentation
├── monitoring/           # Monitoring and alerts
├── prompts/              # RAG prompts and templates
├── published/            # Published content
├── rag/                  # RAG implementation
├── tests/                # Test suites
├── api.py                # API endpoints
├── automation.py         # Automation scripts
├── config.yml            # Configuration file
├── requirements.txt      # Python dependencies
└── README.md             # Project readme
```

## Development Workflow

### Content Generation Pipeline

1. **Story Creation**: Develop satirical stories targeting specific lifestyle trends
2. **File Organization**: Store stories in appropriate week directories (week1, week2, week3)
3. **Metadata**: Include author and theme information in story files
4. **Version Control**: Commit changes with descriptive messages
5. **Documentation**: Update repo_links.txt with new content references

### Weekly Content Cycle

Each week follows this pattern:
- Create 5 satirical stories covering different lifestyle themes
- Commit stories to the content/weekX directory
- Update documentation and tracking systems
- Verify CI/CD workflow passes
- Update project dashboard

## Technical Stack

- **Language**: Python 3.10+
- **Version Control**: Git/GitHub
- **CI/CD**: GitHub Actions
- **Content Format**: Markdown
- **Linting**: Flake8
- **Automation**: Python scripts

## Content Themes

### Week 1-3 Satirical Stories

- Minimalism and organic living
- Cryptocurrency and blockchain hype
- Cats as lifestyle
- Dietary trends (vegan, keto, paleo, carnivore)
- Self-help gurus and coaching industry
- Work-from-home culture
- Online dating algorithms
- Fitness culture and obsession
- Wellness trends and horoscopes
- Parenting challenges in modern society

## Quality Standards

### Code Quality

- Run `flake8` before committing
- Follow PEP 8 style guidelines
- Add meaningful docstrings to functions
- Keep lines under 120 characters

### Content Quality

- Satirical content should be thought-provoking
- Maintain consistent voice and tone
- Use Russian language appropriately
- Avoid offensive stereotypes
- Include author attribution

## CI/CD Pipeline

The GitHub Actions workflow automatically:

1. Checks out the repository
2. Sets up Python environment
3. Installs dependencies
4. Runs flake8 linting
5. Continues even if warnings exist (non-blocking)

**Status**: ✅ All workflows passing

## Deployment Notes

- The pipeline is optimized for a content repository
- No automated testing framework (not applicable for content)
- Linting is optional (non-blocking failures)
- All commits trigger the CI/CD workflow

## Future Enhancements

- [ ] RAG integration for content retrieval
- [ ] API endpoints for content access
- [ ] Social media automation
- [ ] Content analytics dashboard
- [ ] Monetization tracking
- [ ] Multi-language support

## Monitoring & Metrics

- GitHub Actions workflow status
- Commit frequency and messages
- Content file creation timestamps
- Documentation update tracking

## Contributing Guidelines

1. Follow the weekly content cycle
2. Create satirical stories with clear authorship
3. Update documentation after content creation
4. Ensure CI/CD pipeline passes
5. Maintain consistent naming conventions
6. Use descriptive commit messages

## Support & Issues

For questions or improvements:
1. Check existing documentation
2. Review recent commit messages
3. Examine content examples
4. Update relevant documentation

## License

MIT License - See LICENSE file for details
