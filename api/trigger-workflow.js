/**
 * Vercel Serverless Function
 * Triggers GitHub Actions workflow for QIP Dashboard
 *
 * Environment Variables Required:
 * - GITHUB_TOKEN: GitHub Personal Access Token with 'repo' and 'workflow' permissions
 * - ADMIN_PASSWORD_HASH: SHA-256 hash of admin password (hwk)
 */

export default async function handler(req, res) {
  // CORS headers for cross-origin requests
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

  // Handle preflight OPTIONS request
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({
      error: 'Method not allowed',
      message: 'Only POST requests are accepted'
    });
  }

  try {
    // Verify admin password
    const { passwordHash } = req.body;
    const expectedHash = process.env.ADMIN_PASSWORD_HASH;

    if (!expectedHash) {
      console.error('ADMIN_PASSWORD_HASH environment variable not set');
      return res.status(500).json({
        error: 'Server configuration error',
        message: 'Admin password hash not configured'
      });
    }

    if (passwordHash !== expectedHash) {
      console.warn('Unauthorized access attempt');
      return res.status(401).json({
        error: 'Unauthorized',
        message: 'Invalid admin password'
      });
    }

    // Get GitHub token from environment
    const githubToken = process.env.GITHUB_TOKEN;

    if (!githubToken) {
      console.error('GITHUB_TOKEN environment variable not set');
      return res.status(500).json({
        error: 'Server configuration error',
        message: 'GitHub token not configured'
      });
    }

    // Trigger GitHub Actions workflow
    const githubResponse = await fetch(
      'https://api.github.com/repos/moonkaicuzui/qip-dashboard/actions/workflows/auto-update.yml/dispatches',
      {
        method: 'POST',
        headers: {
          'Authorization': `token ${githubToken}`,
          'Accept': 'application/vnd.github.v3+json',
          'Content-Type': 'application/json',
          'User-Agent': 'QIP-Dashboard-Admin'
        },
        body: JSON.stringify({
          ref: 'main'
        })
      }
    );

    // GitHub API returns 204 on success
    if (githubResponse.status === 204) {
      console.log('Workflow triggered successfully');
      return res.status(200).json({
        success: true,
        message: 'Workflow triggered successfully',
        timestamp: new Date().toISOString()
      });
    } else {
      const errorText = await githubResponse.text();
      console.error('GitHub API error:', githubResponse.status, errorText);
      return res.status(500).json({
        error: 'GitHub API error',
        message: `Failed to trigger workflow (status: ${githubResponse.status})`,
        details: errorText
      });
    }

  } catch (error) {
    console.error('Server error:', error);
    return res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
}
