using System;

public static class Program
{
    public static string Answer(string value)
    {
        string normalized = value.Trim().ToUpperInvariant();
        return string.Concat("rf:", normalized);
    }

    public static void Main(string[] args)
    {
        string input = args.Length > 0 ? args[0] : string.Empty;
        Console.WriteLine(Answer(input));
    }
}
