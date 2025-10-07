/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    // En Docker, usar el nombre del servicio. En desarrollo local, usar localhost
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
